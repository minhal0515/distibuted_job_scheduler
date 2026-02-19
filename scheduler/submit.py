import json
import logging
from scheduler.logging_config import setup_logging
setup_logging()
logger = logging.getLogger("worker")
from scheduler.db import get_conn

def submit_job(
    name: str,
    payload: dict,
    priority: int = 0,
    max_retries: int = 3,
    timeout_seconds: int | None = None,
    idempotency_key: str | None = None,
):
    with get_conn() as conn:
        with conn.cursor() as cur:
            with open("scheduler/sql/submit_job.sql", "r") as f:
                sql = f.read()

            cur.execute(
                sql,
                {
                    "name": name,
                    "payload": json.dumps(payload),
                    "priority": priority,
                    "max_retries": max_retries,
                    "timeout_seconds": timeout_seconds,
                    "idempotency_key": idempotency_key,
                },
            )

            job_id = cur.fetchone()[0]
            conn.commit()

            logger.info(f"Submitted job {job_id}")
            return job_id
