from ..service import LoadBalancer
from .templates import service


class TritonLoadBalancer(LoadBalancer):
    @property
    def spec(self):
        return service["spec"]

    @property
    def metadata(self):
        return service["metadata"]
