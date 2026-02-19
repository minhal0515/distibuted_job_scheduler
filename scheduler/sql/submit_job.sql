WITH new_job AS (
    INSERT INTO jobs (
        id,
        name,
        payload,
        schedule_type,
        next_run_at,
        priority,
        max_retries,
        timeout_seconds,
        status
    )
    VALUES (
        gen_random_uuid(),
        %(name)s,
        %(payload)s::jsonb,
        'ONE_TIME',
        NOW(),
        %(priority)s,
        %(max_retries)s,
        %(timeout_seconds)s,
        'ACTIVE'
    )
    RETURNING id
)
INSERT INTO job_runs (
    id,
    job_id,
    attempt,
    status,
    run_after,
    idempotency_key
)
SELECT
    gen_random_uuid(),
    id,
    1,
    'PENDING',
    NOW(),
    %(idempotency_key)s
FROM new_job
RETURNING job_id;
