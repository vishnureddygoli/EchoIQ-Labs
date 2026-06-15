import json
import os
from datetime import datetime, timezone
from redis import Redis
import psycopg
from psycopg.rows import dict_row

QUEUE_NAME = "echoiq:outbound_calls"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://echoiq:echoiq@localhost:5432/echoiq")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def mark_dispatched(call_attempt_id: str) -> None:
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE call_attempts SET call_status='dispatched_mock', dispatched_at=%s WHERE id=%s",
            (datetime.now(timezone.utc), call_attempt_id),
        )
        conn.commit()

def run_worker() -> None:
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    print(f"EchoIQ mock call worker listening on {QUEUE_NAME}")
    while True:
        try:
            item = redis.blpop([QUEUE_NAME], timeout=10)
            if not item:
                continue
            _, raw = item
            job = json.loads(raw)
            print(f"Dispatching mock outbound call: {job}")
            mark_dispatched(job["call_attempt_id"])
        except KeyboardInterrupt:
            print("Worker stopped")
            break
        except Exception as exc:
            print(f"Worker error: {exc}")
