from pydantic import BaseModel
from typing import Optional

class Incident(BaseModel):
    title: str
    description: Optional[str] = None


class IncidentCreate(Incident):
    pass

class IncidentResponse(Incident):
    id: int

