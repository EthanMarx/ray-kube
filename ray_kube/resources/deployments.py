from typing import TYPE_CHECKING, Optional

import kr8s
from kr8s.objects import Deployment

from ..templates import head, worker

if TYPE_CHECKING:
    from .secret import Secret


class RayDeployment(Deployment):
    template = None

    def __init__(
        self,
        image: str,
        memory: str = "4G",
        num_cpus: int = 1,
        num_gpus: Optional[int] = 0,
        label: Optional[str] = None,
        api: Optional[kr8s.api] = None,
        **kwargs,
    ):
        super().__init__(self.template, api=api, **kwargs)
        self.label = label
        self.image = image
        self._api = api
        self.num_cpus = num_cpus
        self.num_gpus = num_gpus
        self.memory = memory
        self.build()

    def is_ready(self):
        self.refresh()
        return self.ready()

    def build(self):
        if self.label is not None:
            self.set_label()
        self.set_resources()
        self.set_image()

    def set_env_from_secret(self, secret: "Secret"):
        container = self["spec"]["template"]["spec"]["containers"][0]
        ref = dict(secretRef=dict(name=secret.name))
        if "envFrom" not in container:
            container["envFrom"] = []
        container["envFrom"].append(ref)

    def set_env(self, env: dict):
        container = self["spec"]["template"]["spec"]["containers"][0]
        container["env"] = []
        for key, value in env.items():
            container["env"].append(dict(name=key, value=value))

    def set_image(self):
        container = self["spec"]["template"]["spec"]["containers"][0]
        container["image"] = self.image

    def set_resources(self):
        resources = self["spec"]["template"]["spec"]["containers"][0][
            "resources"
        ]
        resources["limits"]["cpu"] = self.num_cpus
        resources["requests"]["cpu"] = self.num_cpus
        resources["limits"]["memory"] = self.memory
        resources["requests"]["memory"] = self.memory

    def set_label(self):
        self["metadata"]["name"] += f"-{self.label}"
        self["metadata"]["labels"]["app"] += f"-{self.label}"
        self["spec"]["selector"]["matchLabels"]["app"] += f"-{self.label}"
        self["spec"]["template"]["metadata"]["labels"][
            "app"
        ] += f"-{self.label}"


class RayHeadNode(RayDeployment):
    template = head

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RayWorkerNode(RayDeployment):
    template = worker

    def __init__(
        self,
        *args,
        min_gpu_memory: str = "15000",
        gpus_per_worker: Optional[int] = 1,
        num_workers: Optional[int] = 1,
        **kwargs,
    ):
        self.num_workers = num_workers
        self.gpus_per_worker = gpus_per_worker
        self.min_gpu_memory = min_gpu_memory
        super().__init__(*args, **kwargs)

    def set_resources(self):
        super().set_resources()
        self["spec"]["replicas"] = self.num_workers
        spec = self["spec"]["template"]["spec"]
        spec["affinity"]["nodeAffinity"][
            "requiredDuringSchedulingIgnoredDuringExecution"
        ]["nodeSelectorTerms"][0]["matchExpressions"][0]["values"] = [
            self.min_gpu_memory
        ]
        resources = spec["containers"][0]["resources"]
        resources["limits"]["nvidia.com/gpu"] = self.gpus_per_worker
        resources["requests"]["nvidia.com/gpu"] = self.gpus_per_worker
