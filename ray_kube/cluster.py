import time
from typing import Optional

import kr8s
from kr8s.objects import Deployment, Service

from ray_kube.templates import cluster_ip, head, load_balancer, worker


class KubernetesRayCluster:
    def __init__(
        self,
        image: str,
        num_workers: int = 2,
        gpus_per_worker: int = 1,
        worker_cpus: int = 2,
        head_cpus: int = 2,
        worker_memory: str = "4G",
        head_memory: str = "4G",
        api: Optional[kr8s.api] = None,
        label: Optional[str] = None,
    ):
        """
        Contextmanager class for managing a Ray cluster via Kubernetes.

        ```
        cluster = KubernetesRayCluster(image="rayproject/ray:2.3.0")
        with cluster as cluster:
            ip = cluster.get_load_balancer_ip()
            ray.init(address=f"ray://{ip}:10001")
            # do stuff with ray cluster
            ...
        ```

        Args:
            image:
                Docker image used for both ray head and worker nodes
            num_workers:
                Number of worker nodes to create
            gpus_per_worker:
                Number of GPUs per worker node
            worker_cpus:
                Number of CPUs per worker node
            head_cpus:
                Number of CPUs for head node
            worker_memory:
                Memory for per worker node.
            head_memory:
                Memory for head node.
            api:
                kr8s.api object.
                Defaults to kr8s.api() which will pick up any cached apis.
            label:
                Label to append to name of all resources.
        """

        api = api or kr8s.api()
        self.cluster_ip = Service(cluster_ip, api=api)
        self.head = Deployment(head, api=api)
        self.worker = Deployment(worker, api=api)
        self.load_balancer = Service(load_balancer, api=api)

        self.label = label
        self.image = image
        self.num_workers = num_workers
        self.gpus_per_worker = gpus_per_worker

        self.worker_cpus = worker_cpus
        self.head_cpus = head_cpus

        self.worker_memory = worker_memory
        self.head_memory = head_memory

        self.set_head()
        self.set_worker()
        if self.label is not None:
            self.set_metadata()

    def set_metadata(self):
        self.cluster_ip["metadata"]["labels"]["app"] += f"-{self.label}"
        self.cluster_ip["metadata"]["name"] += f"-{self.label}"

        self.load_balancer["metadata"]["name"] += f"-{self.label}"
        self.load_balancer["spec"]["selector"]["app"] += f"-{self.label}"

        self.head["metadata"]["name"] += f"-{self.label}"
        self.head["metadata"]["labels"]["app"] += f"-{self.label}"
        self.head["spec"]["selector"]["matchLabels"]["app"] += f"-{self.label}"
        self.head["spec"]["template"]["metadata"]["labels"][
            "app"
        ] += f"-{self.label}"

        self.worker["metadata"]["name"] += f"-{self.label}"
        self.worker["metadata"]["labels"]["app"] += f"-{self.label}"
        self.worker["spec"]["selector"]["matchLabels"][
            "app"
        ] += f"-{self.label}"
        self.worker["spec"]["template"]["metadata"]["labels"][
            "app"
        ] += f"-{self.label}"

    def set_head(self):
        head = self.head["spec"]["template"]["spec"]["containers"][0]
        head["image"] = self.image
        resources = self.head["spec"]["template"]["spec"]["containers"][0][
            "resources"
        ]
        resources["limits"]["cpu"] = self.head_cpus
        resources["requests"]["cpu"] = self.head_cpus
        resources["limits"]["memory"] = self.head_memory
        resources["requests"]["memory"] = self.head_memory

    def set_worker(self):
        self.worker["spec"]["replicas"] = self.num_workers

        worker = self.worker["spec"]["template"]["spec"]["containers"][0]
        worker["image"] = self.image

        resources = self.worker["spec"]["template"]["spec"]["containers"][0][
            "resources"
        ]
        resources["limits"]["nvidia.com/gpu"] = self.gpus_per_worker
        resources["requests"]["nvidia.com/gpu"] = self.gpus_per_worker

        resources["limits"]["cpu"] = self.worker_cpus
        resources["requests"]["cpu"] = self.worker_cpus

        resources["limits"]["memory"] = self.head_memory
        resources["requests"]["memory"] = self.head_memory

    def __iter__(self):
        return iter(
            [self.cluster_ip, self.head, self.worker, self.load_balancer]
        )

    def create(self):
        for resource in self:
            resource.create()
        return self

    def delete(self):
        for resource in self:
            resource.delete()
        return self

    def get_load_balancer_ip(self):
        x = Service.get(self.load_balancer.name)
        return x.status.loadBalancer.ingress[0].ip

    def is_ready(self):
        """
        Returns True if head node is ready.
        TODO: maybe require one worker node?
        """
        pods = kr8s.get("pods", namespace=self.head.namespace)
        for pod in pods:
            if "head" in pod.name:
                return pod.ready()
        else:
            raise ValueError("No head node found.")

    def wait(self):
        # TODO: add timeout
        while True:
            time.sleep(1)
            if self.is_ready():
                return

    def __enter__(self, wait: bool = True):
        self.create()
        if wait:
            self.wait()
        return self

    def __exit__(self, *args):
        self.delete()
        return False
