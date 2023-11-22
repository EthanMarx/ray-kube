from typing import Optional

import kr8s
from kr8s.objects import Service

from ..templates import external, internal


class RayInternalService(Service):
    template = internal

    def __init__(
        self, label: Optional[str] = None, api: Optional[kr8s.api] = None
    ):
        super().__init__(self.template, api=api)
        self.label = label
        self.set_metadata()

    def set_metadata(self):
        self["metadata"]["labels"]["app"] += f"-{self.label}"
        self["metadata"]["name"] += f"-{self.label}"


class RayExternalService(Service):
    template = external

    def __init__(
        self, label: Optional[str] = None, api: Optional[kr8s.api] = None
    ):
        super().__init__(self.template, api=api)
        self.label = label
        self.set_metadata()

    def set_metadata(self):
        self["metadata"]["name"] += f"-{self.label}"
        self["spec"]["selector"]["app"] += f"-{self.label}"

    def ip(self):
        self.refresh()
        return self.status.loadBalancer.ingress[0].ip
