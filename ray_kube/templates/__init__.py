from pathlib import Path

import yaml

path = Path(__file__).parent


def load_template(template):
    with open(template) as f:
        template = yaml.safe_load(f)
    return template


head = load_template(path / "head.yaml")
worker = load_template(path / "worker.yaml")
internal = load_template(path / "internal.yaml")
external = load_template(path / "external.yaml")
secret = load_template(path / "secret.yaml")
