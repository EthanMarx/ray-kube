from typing import List

from ..deployment import Deployment
from .templates import servers


class TritonServerDeployment(Deployment):
    def __init__(
        self, *args, command: List[str], command_args: List[str], **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.command = command
        self.set_command()

    def set_args(self):
        self["spec"]["template"]["spec"]["containers"][0][
            "args"
        ] = self.command_args

    def set_command(self):
        self["spec"]["template"]["spec"]["containers"][0][
            "command"
        ] = self.command

    @property
    def spec(self):
        return servers["spec"]

    @property
    def metadata(self):
        return servers["metadata"]
