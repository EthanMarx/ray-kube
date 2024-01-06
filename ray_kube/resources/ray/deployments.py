from ..deployment import Deployment
from .templates import head, worker


class RayHeadNode(Deployment):
    @property
    def spec(self):
        return head["spec"]

    @property
    def metadata(self):
        return head["metadata"]


class RayWorkerNode(Deployment):
    @property
    def spec(self):
        return worker["spec"]

    @property
    def metadata(self):
        return worker["metadata"]
