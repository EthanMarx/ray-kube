from typing import Optional

import kr8s
from kr8s.objects import Service as _Service


class Service(_Service):
    template = {"apiVersion": "v1", "kind": "Service"}

    def __init__(
        self, label: Optional[str] = None, api: Optional[kr8s.api] = None
    ):

        self.template["metadata"] = self.metadata
        self.template["spec"] = self.spec
        super().__init__(self.template, api=api)

        if label is not None:
            self.label = label
            self.add_label()

    @property
    def spec(self):
        return {}

    @property
    def metadata(self):
        return {}

    def add_label(self):
        self["metadata"]["name"] += f"-{self.label}"
        self["spec"]["selector"]["app"] += f"-{self.label}"


class LoadBalancer(Service):
    template = {"apiVersion": "v1", "kind": "Service"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.spec["type"] == "LoadBalancer", (
            " Attempted to create LoadBalancer object without "
            "specifying LoadBalancer as type in spec"
        )

    @property
    def ip(self):
        self.refresh()
        return self.status.loadBalancer.ingress[0].ip
