from pathlib import Path

import yaml

path = Path(__file__).parent


def load_template(template):
    with open(template) as f:
        template = yaml.safe_load(f)
    return template


servers = load_template(path / "servers.yaml")
service = load_template(path / "service.yaml")
# secret = load_template(path / "secret.yaml")
