head = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "deployment-ray-head",
        "labels": {"app": "ray-cluster-head"},
    },
    "spec": {
        "replicas": 1,
        "selector": {
            "matchLabels": {
                "component": "ray-head",
                "type": "ray",
                "app": "ray-cluster-head",
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "component": "ray-head",
                    "type": "ray",
                    "app": "ray-cluster-head",
                }
            },
            "spec": {
                "restartPolicy": "Always",
                "volumes": [
                    {"name": "dshm", "emptyDir": {"medium": "Memory"}}
                ],
                "containers": [
                    {
                        "name": "ray-head",
                        "image": "rayproject/ray:2.3.0",
                        "imagePullPolicy": "Always",
                        "command": ["/bin/bash", "-c", "--"],
                        "args": [
                            "ray start --head --port=6380 --num-cpus=$MY_CPU_REQUEST --dashboard-host=0.0.0.0 --object-manager-port=8076 --node-manager-port=8077 --dashboard-agent-grpc-port=8078 --dashboard-agent-listen-port=52365 --block"
                        ],
                        "ports": [
                            {"containerPort": 6380},  # GCS server
                            {"containerPort": 10001},  # Used by Ray Client
                            {"containerPort": 8265},  # Used by Ray Dashboard
                        ],
                        "volumeMounts": [
                            {"mountPath": "/dev/shm", "name": "dshm"}
                        ],
                        "env": [
                            {
                                "name": "MY_CPU_REQUEST",
                                "valueFrom": {
                                    "resourceFieldRef": {
                                        "resource": "requests.cpu"
                                    }
                                },
                            }
                        ],
                        "resources": {
                            "limits": {"cpu": "1", "memory": "2G"},
                            "requests": {"cpu": "500m", "memory": "2G"},
                        },
                    }
                ],
            },
        },
    },
}

# Deployment for Ray worker nodes
worker = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "deployment-ray-worker",
        "labels": {"app": "ray-cluster-worker"},
    },
    "spec": {
        "replicas": 2,  # i.e. number of workers
        "selector": {
            "matchLabels": {
                "component": "ray-worker",
                "type": "ray",
                "app": "ray-cluster-worker",
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "component": "ray-worker",
                    "type": "ray",
                    "app": "ray-cluster-worker",
                }
            },
            "spec": {
                "restartPolicy": "Always",
                "volumes": [
                    {"name": "dshm", "emptyDir": {"medium": "Memory"}}
                ],
                "containers": [
                    {
                        "name": "ray-worker",
                        "image": "rayproject/ray:2.3.0",
                        "imagePullPolicy": "Always",
                        "command": ["/bin/bash", "-c", "--"],
                        "args": [
                            "ray start --num-cpus=$MY_CPU_REQUEST --address=service-ray-cluster:6380 --object-manager-port=8076 --node-manager-port=8077 --dashboard-agent-grpc-port=8078 --dashboard-agent-listen-port=52365 --block"
                        ],
                        "volumeMounts": [
                            {"mountPath": "/dev/shm", "name": "dshm"}
                        ],
                        "env": [
                            {
                                "name": "MY_CPU_REQUEST",
                                "valueFrom": {
                                    "resourceFieldRef": {
                                        "resource": "requests.cpu"
                                    }
                                },
                            }
                        ],
                        "resources": {
                            "limits": {
                                "cpu": "1",
                                "memory": "1G",
                                "nvidia.com/gpu": 1,
                            },
                            "requests": {
                                "cpu": "500m",
                                "memory": "1G",
                                "nvidia.com/gpu": 1,
                            },
                        },
                    }
                ],
            },
        },
    },
}
