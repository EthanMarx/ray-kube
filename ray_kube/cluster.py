import time
from pathlib import Path
from typing import Optional

import kr8s
import yaml
from resources import (
    RayExternalService,
    RayHeadNode,
    RayInternalService,
    RayWorkerNode,
)


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

        api = api or kr8s.api()
        self.head = RayHeadNode(
            image,
            memory=head_memory,
            num_cpus=head_cpus,
            num_gpus=0,
            label=label,
            api=api,
        )

        self.worker = RayWorkerNode(
            image,
            num_workers=num_workers,
            memory=worker_memory,
            num_cpus=worker_cpus,
            num_gpus=gpus_per_worker,
            label=label,
            api=api,
        )

        self.internal = RayInternalService(
            label=label,
            api=api,
        )

        self.external = RayExternalService(
            label=label,
            api=api,
        )

        self.resources = [
            self.head,
            self.worker,
            self.internal,
            self.external,
        ]

    def add_secret(self, path: Path):
        """
        Add a secret to the cluster from a pre-built manifest,
        and decode the secret data as environment variables
        via `envFrom` syntax in the head and worker deployments.

        Args:
            path:
                Path to pre-built secret manifest.
        """

        # create secret and add to resources
        with open(path) as f:
            secret = yaml.safe_load(f)
        # secret = Secret(secret, api=self.api)
        self.resources.append(secret)

        # decode secret data as environment variables
        # in head and worker deployments via envFrom
        for node in [self.head, self.worker]:
            container = node["spec"]["template"]["spec"]["containers"][0]
            if "envFrom" not in container:
                container["envFrom"] = []
            container["envFrom"].append({"secretRef": {"name": secret.name}})

    def wait(self, timeout: Optional[float] = None):
        count = 0
        while not self.is_ready():
            time.sleep(1)
            count += 1
            if timeout is not None:
                if count > timeout:
                    raise TimeoutError("Cluster failed to start in time")

    def is_ready(self):
        return self.head.is_ready()

    def dump(self, filename: str):
        resources = []
        for resource in self:
            resources.append(resource.raw)
        with open(filename, "w") as f:
            yaml.dump_all(resources, f)

    def create(self):
        for resource in self:
            resource.create()
        return self

    def delete(self):
        for resource in self:
            resource.delete()
        return self

    def __enter__(self, wait: bool = True):
        self.create()
        if wait:
            self.wait()
        return self

    def __exit__(self, *args):
        self.delete()
        return False

    def __iter__(self):
        for resource in self.resources:
            yield resource
