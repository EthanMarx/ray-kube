from kr8s.objects import Secret as _Secret


class Secret:
    template = {"apiVersion": "v1", "kind": "Secret", "type": "Opaque"}

    # construct template in __new__
    # since Secret doesn't support item assignment
    def __new__(cls, name: str, env: dict, *args, **kwargs):
        cls.template["metadata"] = {}
        cls.template["metadata"]["name"] = name
        cls.template["stringData"] = env
        return _Secret(cls.template, *args, **kwargs)
