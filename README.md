# ray-kube
Python `contextmanager` for deploying publicly exposed, static Ray clusters with Kubernetes.

See [this](https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/static-ray-cluster-without-kuberay.html) example from [`ray`](https://docs.ray.io/en/latest/) for the inspiration.

Useful for instances where your kubernetes cluster does not support arbitrary CRD (such as [KubeRay](https://docs.ray.io/en/latest/cluster/kubernetes/index.html)). This is the case for the [Nautilus HyperCluster](https://nationalresearchplatform.org/nautilus/).


# Quickstart
```python
import kr8s
import ray

from ray_kube import KubernetesRayCluster
from ray_kube.utils import refresh_token

# instantiate an api instance that is cached by kr8s
api = kr8s.api(kubeconfig="~/.kube/config")

# initiate a KubernetesRayCluster object
cluster = KubernetesRayCluster(
    image="rayproject/ray:2.8.0-py39", # client and node ray and python minor versions must match
    num_workers = 3,
    gpus_per_worker = 1,
)

# launch the cluster
with cluster as cluster:
    # find external ip address of load balancer,
    # which forwards traffic to ray head node,
    # and then connect to that node
    ip = cluster.get_ip()
    ray.init(address=f"ray://{ip}:10001")
    
    # send a request to the cluster!
    @ray.remote
    def hello_world():
        return "hello world"

    print(ray.get(hello_world.remote()))

    # close connection to cluster
    ray.shutdown()
```


## Adding Secrets
Adding a kubernetes Secret is as simple as 

```python
cluster = KubernetesRayCluster(
    image="rayproject/ray:2.8.0-py39"
)
cluster.add_secret(name="credentials", env={"credentials" : "password"})

# launch cluster ...
```

This will automatically deploy a Secret resource, 
and will set the secret data as enviroment variables
inside the node worker deployments
