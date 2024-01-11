from typing import Optional

import kr8s

from .cluster import Cluster
from .resources.ray import (
    RayExternalService,
    RayHeadNode,
    RayInternalService,
    RayWorkerNode,
)
from .resources.secret import Secret
from .utils import authenticate


class KubernetesRayCluster(Cluster):
    def __init__(
        self,
        image: str,
        num_workers: int = 2,
        gpus_per_worker: int = 1,
        worker_cpus: int = 2,
        head_cpus: int = 2,
        worker_memory: str = "4G",
        head_memory: str = "4G",
        min_gpu_memory: str = "15000",
        api: Optional[kr8s.api] = None,
        label: Optional[str] = None,
        namespace: Optional[str] = None,
    ):

        api = api or kr8s.api()
        api.auth.reauthenticate = authenticate.__get__(
            api.auth, type(api.auth)
        )

        self.head = RayHeadNode(
            image,
            memory=head_memory,
            cpus_per_replica=head_cpus,
            label=label,
            api=api,
        )

        self.worker = RayWorkerNode(
            image,
            min_gpu_memory=min_gpu_memory,
            num_replicas=num_workers,
            memory=worker_memory,
            cpus_per_replica=worker_cpus,
            gpus_per_replica=gpus_per_worker,
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

        if namespace is not None:
            for resource in self:
                resource.namespace = namespace

    def add_secret(self, name: str, env: dict):
        """
        Add a secret to the deployment with name `name` and
        set it's `stringData` field to `env`.

        Decode the secret in head and worker nodes
        with the `envFrom` syntax
        """

        secret = Secret(name, env)
        self.resources.append(secret)

        # decode secret data as environment variables
        # in head and worker deployments via envFrom
        self.head.set_env_from_secret(secret)
        self.worker.set_env_from_secret(secret)

    def set_env(self, env: dict):
        """
        Set the environment variables in the head and worker deployments
        """
        self.head.set_env(env)
        self.worker.set_env(env)

    def is_ready(self):
        return self.head.is_ready()
