from ray.job_submission import JobSubmissionClient, JobStatus
import time
import subprocess
from kubernetes import client, config

COMPLETE = {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}
def get_kubernetes_load_balancer_ip():
    config.load_kube_config()
    api = client.CoreV1Api()
    service = api.read_namespaced_service(name="ray-head-loadbalancer", namespace="bbhnet")
    return service.status.load_balancer.ingress[0].ip


def main():
    service_ip = get_kubernetes_load_balancer_ip()
    ray_client = JobSubmissionClient(f"http://{service_ip}:8265")
    job_id = ray_client.submit_job(
        entrypoint="echo 'hello world'",
    )

    def wait_until_status(job_id: str, timeout_seconds=5):
        start = time.time()
        while time.time() - start <= timeout_seconds:
            status = ray_client.get_job_status(job_id)
            print(f"status: {status}")
            if status in COMPLETE:
                break
            time.sleep(1)


    wait_until_status(job_id, )
    logs = ray_client.get_job_logs(job_id)
    print(logs)

if __name__ == "__main__":
    main()


