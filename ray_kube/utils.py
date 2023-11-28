import subprocess


# used to monkey patch kr8s api refresh method;
# see https://github.com/kr8s-org/kr8s/issues/214
async def authenticate(self):
    """
    Replacement reauthenticate method that
    uses kubectl to refresh the OIDC token
    """
    subprocess.run(
        ["kubectl", "cluster-info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    await self._load_kubeconfig()
