from pathlib import Path
import yaml
from kubernetes import utils, config, client
from kubernetes.client.rest import ApiException
from typing import Optional
from contextlib import contextmanager
from kr8s.objects import Deployment, Service
import kr8s
from dataclasses import dataclass
from httpx import HTTPStatusError

BASE_DEPLOYMENT = Path(__file__).parent / "deploy.yaml" 

class Resource:
    def __new__(self, config, api):
        if config["kind"] == "Deployment":
            cls = Deployment
        elif config["kind"] == "Service":
            cls = Service
        return cls(config, api=api)

@dataclass
class RayCluster:
    cluster_ip: Service
    head: Deployment
    worker: Deployment
    load_balancer: Service

    def __iter__(self):
        return iter([self.cluster_ip, self.head, self.worker, self.load_balancer])

class KubernetesRayCluster:
    def __init__(
        self, 
        num_workers: int, 
        image: str,
        namespace: str = "default",
    ):
        self.num_workers = num_workers
        self.image = image
        self.namespace = namespace
        self.api = kr8s.api(kubeconfig="~/.kube/config")
        self.resources = self.load_resources()
        self.build()

    def load_resources(self):
        resources = []
        with open(BASE_DEPLOYMENT) as f:
            content = yaml.safe_load_all(f)
            for doc in content:
                x = Resource(doc, api=self.api)
                resources.append(x)
        return RayCluster(*resources)
    
    def build(self):
        # set image of head node and worker nodes,
        # set number of replicas of workers based on request
        self.resources.head["spec"]["template"]["spec"]["containers"][0]["image"] = self.image
        self.resources.worker["spec"]["template"]["spec"]["containers"][0]["image"] = self.image
        self.resources.worker["spec"]["replicas"] = self.num_workers
       
    def delete(self):
        for resource in self.resources:
            resource.delete()
        
    # TODO: 
    # probably should just use __enter__ and __exit__
    @contextmanager
    def create(self):
        # catch all errors
        try:
            for resource in self.resources:
                resource.create()
            yield self
        finally:
            self.delete()

    def get_load_balancer_ip(self):
        x = Service.get(self.resources.load_balancer.name)
        return x.status.loadBalancer.ingress[0].ip