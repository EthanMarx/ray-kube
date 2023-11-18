# ray-kube
Deploy publicly exposed static Ray clusters with Kubernetes

# Quickstart
Launch the kubernetes pods and services with 

```
kubectl apply -f deploy.yaml
```

Once pods are running, you can make a simple hello world request with

```
poetry run python ray_kube/request.py
```
