from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes.incidents import incident_router
from .routes.health import health_router
from .db import init_pg_pool, close_pg_pool, init_redis, close_redis



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pg_pool()
    await init_redis()

    yield

    await close_redis()
    await close_pg_pool()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incident_router)
app.include_router(health_router)

