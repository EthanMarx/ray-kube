from ray.job_submission import JobSubmissionClient, JobStatus
import utils as ray_kube_utils
from cluster import KubernetesRayCluster


def main(
    entrypoint: str,
    image: str,
    namespace: str = "bbhnet",
    num_workers: int = 2,
):
    """
    entrypoint: path to python file to run
    """

    # create a kubernetes ray cluster
    cluster = KubernetesRayCluster(
        image=image,
        num_workers=num_workers,
        namespace=namespace,
    )


    with cluster.create() as cluster:
        # find external ip of load balancer service
        # and connect a ray job submission client to it
        ip = cluster.get_load_balancer_ip()
        ray_client = JobSubmissionClient(f"http://{ip}:8265")

        # entrypoint will be call to tune.Tuner.fit()
        job_id = ray_client.submit_job(
            entrypoint=entrypoint,
        )

        ray_kube_utils.wait_until_status(ray_client, job_id)
        logs = ray_client.get_job_logs(job_id)

if __name__ == "__main__":
    main()


