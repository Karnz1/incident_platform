from fastapi import Depends, APIRouter
import json
from psycopg import AsyncConnection
import redis.asyncio as redis

from ..models.schemas import IncidentCreate 
from ..db import get_pg_db, get_redis_client

#constants
INCIDENT_REVIEW_QUEUE = "queues:incident_review"

incident_router = APIRouter()

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
                "process_incident"
            )
        )

        row = await cur.fetchone()

    await pg.commit()

    incident_id = row["id"]

    await redis_client.rpush(
        INCIDENT_REVIEW_QUEUE,
        str(incident_id),
    )
    
    return {"id": incident_id, "status": "queued"}


@incident_router.get("/incidents")
def get_all_incidents():
    return "ALL incidents"


@incident_router.patch("/incident/{id}")
def update_incident(id: str):
    return "updated incident"

@incident_router.delete("/incidents/{id}")
def delete_incident(id: str):
    return "deleted incident"