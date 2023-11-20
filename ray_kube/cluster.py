from ray_kube.templates import head, worker, cluster_ip, load_balancer
import kr8s
from kr8s.objects import Deployment, Service


class KubernetesRayCluster:
    api = kr8s.api(kubeconfig="~/.kube/config")
    cluster_ip = Service(cluster_ip)
    head = Deployment(head)
    worker = Deployment(worker)
    load_balancer = Service(load_balancer)

    def __init__(
        self, 
        num_workers: int, 
        image: str,
        gpus_per_worker: int
    ):
        # set image of head node and worker nodes,
        # set number of replicas of workers,
        # set number of gpus per worker
        self.head["spec"]["template"]["spec"]["containers"][0]["image"] = image
        self.worker["spec"]["template"]["spec"]["containers"][0]["image"] = image
        self.worker["spec"]["replicas"] = num_workers
        self.worker["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = gpus_per_worker
        self.image = image
        self.num_workers = num_workers
    
    def __iter__(self):
        return iter([self.cluster_ip, self.head, self.worker, self.load_balancer])

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

    def __enter__(self):
        return self.create()
    
    def __exit__(self, *args):
        self.delete()
        return False
    
    
