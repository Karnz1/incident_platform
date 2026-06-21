from fastapi import Depends, APIRouter, HTTPException
from psycopg import AsyncConnection
import redis.asyncio as redis
from ..models.schemas import IncidentCreate, Severity
from ..db import get_pg_db, get_redis_client
from ..metrics import incidents_created

# constants
INCIDENT_REVIEW_QUEUE = "queues:incident_review"

incident_router = APIRouter()


def severity_int_to_name(severity_value):
    """Convert severity integer to enum name."""
    if severity_value is None:
        return None
    try:
        return Severity(severity_value).name
    except ValueError:
        return None


def severity_int_to_color(severity_value):
    """Convert severity integer to color code."""
    color_map = {
        1: "#ef4444",  # CRITICAL - red
        2: "#f97316",  # HIGH - orange
        3: "#eab308",  # MEDIUM - yellow
        4: "#22c55e",  # LOW - green
    }
    return color_map.get(severity_value, "#6b7280")  # gray default

@incident_router.get("/incidents/{id}")
async def get_incident(id: str):
    return "return specific incident"

# add an incident
@incident_router.post("/incidents")
async def create_incident(
        incident: IncidentCreate,
        pg: AsyncConnection = Depends(get_pg_db),
        redis_client: redis.Redis = Depends(get_redis_client)
):
    title, description = incident.title, incident.description
    async with pg.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO incidents (title, description, status)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (
                title,
                description,
                "queued"
            )
        )

        row = await cur.fetchone()

    await pg.commit()
    incidents_created.inc()
    incident_id = row["id"]

    await redis_client.rpush(
        INCIDENT_REVIEW_QUEUE,
        str(incident_id),
    )
    
    return {"id": incident_id, "status": "queued"}


@incident_router.get("/incidents")
async def get_all_incidents(pg: AsyncConnection = Depends(get_pg_db)):
    async with pg.cursor() as cur:
        await cur.execute(
            """
            SELECT id, title, description, status, severity, sla_deadline, processed_at
            FROM incidents
            ORDER BY id DESC
            """
        )
        rows = await cur.fetchall()

    return [
        {
            **row,
            "severity": severity_int_to_name(row["severity"]),
            "severity_color": severity_int_to_color(row["severity"]),
        }
        for row in rows
    ]


@incident_router.patch("/incident/{id}")
def update_incident(id: str):
    return "updated incident"

@incident_router.delete("/incidents/{id}")
async def delete_incident(id: int, pg: AsyncConnection = Depends(get_pg_db)):
    async with pg.cursor() as cur:
        await cur.execute(
            "DELETE FROM incidents WHERE id = %s RETURNING id",
            (id,),
        )
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    await pg.commit()

    return {"id": id}