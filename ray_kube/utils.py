import subprocess


def refresh_oicd_token():
    """
    Dummy call to kubectl to refresh the kubernetes oicd token.
    See https://github.com/kr8s-org/kr8s/issues/125 and
    https://github.com/kr8s-org/kr8s/issues/214
    """
    subprocess.run(
        ["kubectl", "cluster-info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
