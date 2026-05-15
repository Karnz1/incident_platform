# app/worker.py
import asyncio
import logging
import signal
from datetime import datetime, timezone
import re
from app.api.db import init_pg_pool, close_pg_pool, init_redis, close_redis



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger("incident-worker")

SEVERITY_RULES = {
    "CRITICAL": {
        "sla_hours": 1,
        "keywords": [
            "down",
            "system down",
            "service down",
            "not working",
            "unavailable",
            "outage",
            "production outage",
            "cannot access",
            "data loss",
            "security breach",
            "payment failure",
            "all users",
            "no one can",
        ],
    },
    "HIGH": {
        "sla_hours": 2,
        "keywords": [
            "slow",
            "very slow",
            "degraded",
            "timeout",
            "timeouts",
            "failed",
            "failing",
            "major issue",
            "many users",
            "intermittent",
            "critical customer",
            "blocked",
        ],
    },
    "MEDIUM": {
        "sla_hours": 4,
        "keywords": [
            "error",
            "bug",
            "issue",
            "problem",
            "incorrect",
            "wrong",
            "cannot complete",
            "partial failure",
            "some users",
        ],
    },
    "LOW": {
        "sla_hours": 6,
        "keywords": [
            "question",
            "request",
            "how to",
            "minor",
            "cosmetic",
            "typo",
            "improvement",
            "feature request",
        ],
    },
}


DEFAULT_SEVERITY = "LOW"
QUEUE_NAME = "incidents_queue"

shutdown_event = asyncio.Event()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def determine_severity_and_sla(title: str, description: str):
    combined_text = normalize_text(f"{title} {description}")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        rule = SEVERITY_RULES[severity]
        for keyword in rule["keywords"]:
            if keyword in combined_text:
                return severity, rule["sla_hours"]
    
    return DEFAULT_SEVERITY, 1


async def fetch_incident(conn, incident_id: int):
    return await conn.fetchrow(
        """
        SELECT id, title, description
        FROM incidents
        WHERE id = $1
        """,
        incident_id,
    )


async def update_incident(conn, incident_id: int, severity: str, sla_deadline):
    await conn.execute(
        """
        UPDATE incidents
        SET
            status = $1,
            severity = $2,
            sla_deadline = $3,
            processed_at = $4
        WHERE id = $5
        """,
        "processed",
        severity,
        sla_deadline,
        datetime.now(timezone.utc),
        incident_id,
    )


async def process_incident(incident_id: int, pg_pool):
    async with pg_pool.acquire() as conn:
        incident = await fetch_incident(conn, incident_id)

        if incident is None:
            logger.warning("Incident %s not found in PostgreSQL", incident_id)
            return

        title = incident["title"] or ""
        description = incident["description"] or ""

        severity, sla_deadline = determine_severity_and_sla(title, description)

        await update_incident(
            conn=conn,
            incident_id=incident_id,
            severity=severity,
            sla_deadline=sla_deadline,
        )

        logger.info(
            "Processed incident %s with severity=%s sla_deadline=%s",
            incident_id,
            severity,
            sla_deadline,
        )


async def worker_loop():
    pg_pool = await init_pg_pool()
    redis_client = init_redis()

    logger.info("Incident worker started. Listening on queue: %s", QUEUE_NAME)

    while not shutdown_event.is_set():
        try:
            item = await redis_client.brpop(QUEUE_NAME, timeout=5)

            if item is None:
                continue

            queue_name, raw_incident_id = item

            try:
                incident_id = int(raw_incident_id)
            except ValueError:
                logger.warning("Invalid incident ID from Redis: %s", raw_incident_id)
                continue

            logger.info("Received incident ID: %s", incident_id)

            await process_incident(incident_id, pg_pool)

        except Exception:
            logger.exception("Unexpected worker error")
            await asyncio.sleep(2)

    logger.info("Worker shutdown requested")

    await close_redis()
    await close_pg_pool()

    logger.info("Worker stopped")


def request_shutdown():
    logger.info("Shutdown signal received")
    shutdown_event.set()


async def main():
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, request_shutdown)

    await worker_loop()


if __name__ == "__main__":
    asyncio.run(main())