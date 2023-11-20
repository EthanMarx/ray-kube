# ray-kube
Python `contextmanager` for deploying publicly exposed, static Ray clusters with Kubernetes. 
See [this](https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/static-ray-cluster-without-kuberay.html) example from ray for the inspiration

# Quickstart


```python
import ray
from ray_kube.cluster import KubernetesRayCluster
import kr8s

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
    ip = cluster.get_load_balancer_ip()
    ray.init(address=f"ray://{ip}:10001")
    
    # send a request to the cluster!
    @ray.remote
    def hello_world():
        return "hello world"

    print(ray.get(hello_world.remote()))
```
