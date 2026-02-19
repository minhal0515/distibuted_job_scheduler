import time
import logging
from scheduler.logging_config import setup_logging
from scheduler.db import get_conn
from pathlib import Path
SQL_DIR = Path(__file__).parent / "sql"
def load_sql(name):
    return (SQL_DIR / name).read_text()
setup_logging()
logger = logging.getLogger("worker")
CLAIM_SQL = load_sql("claim_job.sql")
def run_worker(worker_id: str, poll_interval: int = 2):
    while True:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(CLAIM_SQL, (worker_id,))
                row = cur.fetchone()
                if not row:
                    logger.info("No job to run")
                    time.sleep(poll_interval)
                    continue
                job_run_id, job_id, idempotency_key = row
                logger.info(f"Claimed job_run {job_run_id}")
                logger.info("Simulating job execution...")
                
                if idempotency_key:
                    cur.execute(
                    """
                    SELECT 1
                    FROM job_runs
                    WHERE job_id = %s
                    AND idempotency_key = %s
                    AND status = 'SUCCESS'
                    AND id != %s
                    LIMIT 1
                    """,
                    (job_id, idempotency_key, job_run_id),
                )

                duplicate = cur.fetchone()

                if duplicate:
                logger.info("Duplicate execution detected. Skipping execution.")

                cur.execute(
                    """
                    UPDATE job_runs
                    SET status = 'SUCCESS',
                        finished_at = NOW()
                    WHERE id = %s
                    """,
                    (job_run_id,),
                )
                conn.commit()
                continue

                #TODO: Simulate job execution here
                try:
                    cur.execute(
                            """
                            UPDATE job_runs
                            SET status = 'SUCCESS',
                                finished_at = NOW()
                            WHERE id = %s
                            """,
                            (job_run_id,),
                        )
                    conn.commit()
                    logger.info("Job completed")

                except Exception as e:
                    logger.error(f"Job failed: {e}")
                    cur.execute(
                        """
                        UPDATE job_runs
                        SET status = 'FAILED',
                            finished_at = NOW()
                        WHERE id = %s
                        """,
                        (job_run_id,),
                    )
                    conn.commit()
                    logger.info("Job marked as failed")
