from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes.incidents import incident_router
from .routes.health import health_router
from prometheus_client import make_asgi_app
from api import metrics # noqa: F401 — importing registers the metrics
from .db import init_pg_pool, close_pg_pool, init_redis, close_redis
import os

print("this is a test")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "1":
        await init_pg_pool()
        await init_redis()

    yield
    if os.getenv("TESTING") != "1":
        await close_redis()
        await close_pg_pool()


app = FastAPI(lifespan=lifespan)

app.mount("/metrics", make_asgi_app())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "dev.local",
        "staging.local",
        "prod.local"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incident_router, prefix="/api")
app.include_router(health_router)

