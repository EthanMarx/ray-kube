from ray.job_submission import JobSubmissionClient, JobStatus
import time
import logging

COMPLETE = {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}


def wait_until_status(client: JobSubmissionClient, job_id: str, timeout_seconds=5):
    start = time.time()
    while time.time() - start <= timeout_seconds:
        status = client.get_job_status(job_id)
        logging.debug(f"Job {job_id} status: {status}")
        if status in COMPLETE:
            break
        time.sleep(1)