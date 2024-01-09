from ..deployment import Deployment
from .templates import servers


class TritonServerDeployment(Deployment):
    """
    Simple subclass that defines
    spec and metadata for triton server
    deployment from templates
    """

    @property
    def spec(self):
        return servers["spec"]

    @property
    def metadata(self):
        return servers["metadata"]
