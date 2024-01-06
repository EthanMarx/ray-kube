import time
from typing import Optional

import yaml


class Cluster:
    def add_secret(self, name: str, env: dict):
        raise NotImplementedError

    def set_env(self, env: dict):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def wait(self, timeout: Optional[float] = None):
        count = 0
        while not self.is_ready():
            time.sleep(1)
            count += 1
            if timeout is not None:
                if count > timeout:
                    raise TimeoutError("Cluster failed to start in time")

    def dump(self, filename: str):
        resources = []
        for resource in self:
            resources.append(resource.raw)
        with open(filename, "w") as f:
            yaml.dump_all(resources, f)

    def create(self):
        for resource in self:
            resource.create()
        return self

    def delete(self):
        for resource in self:
            resource.delete()
        return self

    def __enter__(self, wait: bool = True):
        self.create()
        if wait:
            self.wait()
        return self

    def get_ip(self):
        """
        Get the ip of the load balancer
        that forwards traffic to the head node
        """
        return self.external.ip

    def __exit__(self, *args):
        self.delete()
        return False

    def __iter__(self):
        for resource in self.resources:
            yield resource
