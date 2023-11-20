import ray

from ray_kube.deploy import KubernetesRayCluster


# TODO: currently a mismatch of python versions
# between ray deployed on kubernetes and ray locally
# will cause issues. Should we call ray.init() and
# tuner.fit() inside the container as well?
def main(tuner: ray.tune.Tuner, image: str, num_workers: int = 2):
    """
    Deploy a ray cluster via kubernetes, and execute a
    ray.tune hyperparameter search via ray.tune.Tuner on it.

    tuner:
        A pre configured ray.tune.Tuner object,
        ready for .fit() to be called.
    image:
        The docker image to use for ray head and worker nodes.
        Must have ray installed.
    num_workers:
        The number of ray workers to use in the cluster.
    """

    # create a kubernetes ray cluster
    cluster = KubernetesRayCluster(
        image=image,
        num_workers=num_workers,
    )

    with cluster as cluster:
        # find external ip of load balancer service
        # and connect a ray job submission client to it
        ip = cluster.get_load_balancer_ip()
        ray.init(address=f"ray://{ip}:10001")
        results = tuner.fit()

    return results


if __name__ == "__main__":
    main()
