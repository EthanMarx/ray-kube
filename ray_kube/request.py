from ray.job_submission import JobSubmissionClient, JobStatus
import time
import subprocess
from kubernetes import client, config

# 10.100.0.1
# TODO: do this with kubernetes API
def get_kubernetes_load_balancer_ip():
    config.load_kube_config()
    api = client.CoreV1Api()
    service = api.read_namespaced_service(name="ray-head-loadbalancer", namespace="bbhnet")
    return service.status.load_balancer.ingress[0].ip

service_ip = get_kubernetes_load_balancer_ip()

ray_client = JobSubmissionClient(f"http://{service_ip}:8265")
job_id = ray_client.submit_job(
    entrypoint="echo 'hello'",
    #runtime_env={"working_dir": "./"}
)

def wait_until_status(job_id, status_to_wait_for, timeout_seconds=5):
    start = time.time()
    while time.time() - start <= timeout_seconds:
        status = ray_client.get_job_status(job_id)
        print(f"status: {status}")
        if status in status_to_wait_for:
            break
        time.sleep(1)


wait_until_status(job_id, {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED})
logs = ray_client.get_job_logs(job_id)
print(logs)

