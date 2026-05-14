from fastapi import Depends, APIRouter


incident_router = APIRouter()

@incident_router.get("/incidents/{id}")
def get_incident(id: str):
    return "return specific incident"


@incident_router.post("/incidents")
def create_incident(incident: dict):
    return "incident created"


@incident_router.get("/incidents")
def get_all_incidents():
    return "ALL incidents"


@incident_router.patch("/incident/{id}")
def update_incident(id: str):
    return "updated incident"

@incident_router.delete("/incidents/{id}")
def delete_incident(id: str):
    return "deleted incident"