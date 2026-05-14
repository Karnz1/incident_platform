from pydantic import BaseModel, Field
from typing import Optional
from enum import IntEnum
from datetime import datetime


class Severity(IntEnum):
    LOW = 4
    MEDIUM = 3
    HIGH = 2
    CRITICAL = 1

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=50, description="Title of the incident")
    description: str = Field(..., min_length=3, max_length=512, description="Description of the incident")
    #severity: Optional[Severity] = Field(None, description="The severity of the incident")


class Incident(IncidentBase):
    id: int = Field(..., description="Unique identifier of the incident")


class IncidentCreate(IncidentBase):
    pass


class SaveIncidentDB(Incident):
    severity: Severity = Field(None, description="The severity of the incident")
    status: str = Field(default="queued", description="the status of the incident")
    sla_deadline: datetime = Field(None, description="The SLA deadline for the incident")


class WorkerUpdateIncident(IncidentBase):
    severity: Severity = Field(..., description="The severity of the incident")
    status: str = Field(..., description="the status of the incident")
    sla_deadline: datetime = Field(..., description="The SLA deadline for the incident")


class QueueToRedis(BaseModel):
    id: int = Field(..., description="Unique identifier of the incident")
    job_type: str = Field(default="process_incident", description="")





