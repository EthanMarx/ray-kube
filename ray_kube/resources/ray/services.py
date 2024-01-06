from ..service import LoadBalancer, Service
from .templates import external, internal


class RayInternalService(Service):
    @property
    def spec(self):
        return internal["spec"]

    @property
    def metadata(self):
        return internal["metadata"]


class RayExternalService(LoadBalancer):
    @property
    def spec(self):
        return external["spec"]

    @property
    def metadata(self):
        return external["metadata"]
