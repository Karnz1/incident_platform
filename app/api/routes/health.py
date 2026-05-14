
from fastapi import Depands, APIRouter

health_router =  APIRouter()

@health_router.get("/ready")
def dep_ready():
    return "dependencies check"


@health_router.get("/health")
def health_check():
    return {"status": "ok"}


@health_router.get("/metrics")
def get_metrics():
    return "return prometheus metrics"
