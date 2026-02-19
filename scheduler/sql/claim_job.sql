WITH candidate AS (
    SELECT jr.id
    FROM job_runs jr
    JOIN jobs j ON j.id = jr.job_id
    WHERE jr.status = 'PENDING'
      AND jr.run_after <= NOW()
      AND j.status = 'ACTIVE'
    ORDER BY j.priority DESC, jr.created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
UPDATE job_runs
SET
    status = 'RUNNING',
    worker_id = %s,
    locked_at = NOW(),
    lock_expires_at = NOW() + INTERVAL '5 minutes',
    started_at = NOW()
WHERE id IN (SELECT id FROM candidate)
RETURNING id, job_id, idempotency_key;