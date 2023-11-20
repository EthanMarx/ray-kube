import kr8s
from kr8s.objects import Deployment, Service

from ray_kube.templates import cluster_ip, head, load_balancer, worker


class KubernetesRayCluster:
    def __init__(
        self, image: str, num_workers: int = 2, gpus_per_worker: int = 1
    ):

        self.cluster_ip = Service(cluster_ip, api=kr8s.api())
        self.head = Deployment(head, api=kr8s.api())
        self.worker = Deployment(worker, api=kr8s.api())
        self.load_balancer = Service(load_balancer, api=kr8s.api())

        self.image = image
        self.num_workers = num_workers
        self.gpus_per_worker = gpus_per_worker

        self.set_image()
        self.set_worker()

    def set_image(self):
        head = self.head["spec"]["template"]["spec"]["containers"][0]
        head["image"] = self.image

        worker = self.worker["spec"]["template"]["spec"]["containers"][0]
        worker["image"] = self.image

    def set_worker(self):
        self.worker["spec"]["replicas"] = self.num_workers
        resources = self.worker["spec"]["template"]["spec"]["containers"][0][
            "resources"
        ]
        resources["limits"]["nvidia.com/gpu"] = self.gpus_per_worker
        resources["requests"]["nvidia.com/gpu"] = self.gpus_per_worker

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

    def __enter__(self):
        return self.create()

    def __exit__(self, *args):
        self.delete()
        return False
