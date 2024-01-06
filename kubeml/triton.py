from typing import Optional

import kr8s
from kr8s.objects import Secret

from .resources.triton import TritonLoadBalancer, TritonServerDeployment
from .utils import authenticate


class KubernetesTritonCluster:
    """
    Launch a cluster of Triton Servers on a Kubernetes Cluster.

    Args:
        image:
            The docker image to use for the Triton Server
        command:
            The command to run in the Triton Server container
        num_replicas:
            The number of Triton Server replicas to launch
        gpus_per_replica:
            The number of GPUs to allocate per Triton Server replica
        cpus_per_replica:
            The number of CPUs to allocate per Triton Server replica
        memory:
            The amount of memory to allocate per Triton Server replica
        min_gpu_memory:
            The minimum amount of GPU memory to allocate
            per Triton Server replica
        api:
            The Kubernetes API to use. Defaults to the default API.
        label:
            The label to apply to all resources created by this cluster
    """

    def __init__(
        self,
        image: str,
        command: str,
        num_replicas: int = 2,
        gpus_per_replica: int = 1,
        cpus_per_replica: int = 2,
        memory: str = "4G",
        min_gpu_memory: str = "15000",
        api: Optional[kr8s.api] = None,
        label: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        api = api or kr8s.api()
        api.auth.reauthenticate = authenticate.__get__(
            api.auth, type(api.auth)
        )

        self.deployment = TritonServerDeployment(
            image,
            num_replicas,
            memory,
            cpus_per_replica,
            gpus_per_replica,
            min_gpu_memory,
            label,
            api,
            command=command,
        )
        self.external = TritonLoadBalancer(
            label=label,
            api=api,
        )

        self.resources = [
            self.deployment,
            self.external,
        ]

    def is_ready(self, how: str = "any"):
        return self.deployment.is_ready()

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
        self.deployment.set_env_from_secret(secret)

    def set_env(self, env: dict):
        """
        Set the environment variables in the head and worker deployments
        """
        self.deployment.set_env(env)
