# internal service for comm between ray head and workers
cluster_ip = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "service-ray-cluster",
        "labels": {
            "app": "ray-cluster-head"
        }
    },
    "spec": {
        "clusterIP": "None",
        "ports": [
            {
                "name": "client",
                "protocol": "TCP",
                "port": 10001,
                "targetPort": 10001
            },
            {
                "name": "dashboard",
                "protocol": "TCP",
                "port": 8265,
                "targetPort": 8265
            },
            {
                "name": "gcs-server",
                "protocol": "TCP",
                "port": 6380,
                "targetPort": 6380
            }
        ],
        "selector": {
            "app": "ray-cluster-head"
        }
    }
}

# Load balancer to expose Ray head node
load_balancer = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "ray-head-loadbalancer"
    },
    "spec": {
        "type": "LoadBalancer",
        "ports": [
            {
                "name": "client",
                "protocol": "TCP",
                "port": 10001,
                "targetPort": 10001
            }
        ],
        "selector": {
            "app": "ray-cluster-head"
        }
    }
}

