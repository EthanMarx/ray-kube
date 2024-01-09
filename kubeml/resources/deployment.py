from typing import List, Optional

import kr8s
from kr8s.objects import Deployment as _Deployment


class Deployment(_Deployment):
    """
    A base class for deployments.
    Contains additional methods for setting
    environment variables, secrets and resources

    Subclasses should inherit from this class and define
    the `spec` and `metadata` methods according to their usecase
    """

    template = {"apiVersion": "apps/v1", "kind": "Deployment"}

    def __init__(
        self,
        image: str,
        command: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        num_replicas: int = 1,
        memory: str = "4G",
        cpus_per_replica: int = 1,
        gpus_per_replica: Optional[int] = None,
        min_gpu_memory: Optional[str] = None,
        label: Optional[str] = None,
        api: Optional[kr8s.api] = None,
        **kwargs,
    ):
        self.template["metadata"] = self.metadata
        self.template["spec"] = self.spec

        super().__init__(self.template, api=api, **kwargs)
        self.command = command
        self.args = args
        self.label = label
        self.image = image
        self._api = api
        self.cpus_per_replica = cpus_per_replica
        self.gpus_per_replica = gpus_per_replica
        self.min_gpu_memory = min_gpu_memory
        self.memory = memory
        self.num_replicas = num_replicas
        self.build()

    @property
    def spec(self):
        return {}

    @property
    def metadata(self):
        return {}

    def is_ready(self):
        self.refresh()
        return self.ready()

    def build(self):
        if self.label is not None:
            self.set_label()
        self.set_resources()
        self.set_image()
        self.set_replicas()
        self.set_command()

    def set_command(self):
        if self.args is not None:
            self["spec"]["template"]["spec"]["containers"][0][
                "args"
            ] = self.args
        if self.command is not None:
            self["spec"]["template"]["spec"]["containers"][0][
                "command"
            ] = self.command

    def set_replicas(self):
        self["spec"]["replicas"] = self.num_replicas

    def set_env_from_secret(self, secret):
        container = self["spec"]["template"]["spec"]["containers"][0]
        ref = dict(secretRef=dict(name=secret.name))
        if "envFrom" not in container:
            container["envFrom"] = []
        container["envFrom"].append(ref)

    def set_env(self, env: dict):
        """
        Set environment variables in the container,
        being careful not to override anything that
        may have already been set in the spec template
        """
        container = self["spec"]["template"]["spec"]["containers"][0]
        try:
            current = container["env"]
        except KeyError:
            current = []
        for key, value in env.items():
            current.append(dict(name=key, value=value))
        container["env"] = current

    def set_image(self):
        container = self["spec"]["template"]["spec"]["containers"][0]
        container["image"] = self.image

    def set_resources(self):
        resources = self["spec"]["template"]["spec"]["containers"][0][
            "resources"
        ]
        resources["limits"]["cpu"] = self.cpus_per_replica
        resources["requests"]["cpu"] = self.cpus_per_replica
        resources["limits"]["memory"] = self.memory
        resources["requests"]["memory"] = self.memory

        if self.gpus_per_replica is not None:
            resources["limits"]["nvidia.com/gpu"] = self.gpus_per_replica
            resources["requests"]["nvidia.com/gpu"] = self.gpus_per_replica

        if self.min_gpu_memory is not None:
            spec = self["spec"]["template"]["spec"]
            spec["affinity"]["nodeAffinity"][
                "requiredDuringSchedulingIgnoredDuringExecution"
            ]["nodeSelectorTerms"][0]["matchExpressions"][0]["values"] = [
                self.min_gpu_memory
            ]

    def set_label(self):
        self["metadata"]["name"] += f"-{self.label}"
        self["metadata"]["labels"]["app"] += f"-{self.label}"

        self["spec"]["selector"]["matchLabels"]["app"] += f"-{self.label}"
        self["spec"]["template"]["metadata"]["labels"][
            "app"
        ] += f"-{self.label}"
