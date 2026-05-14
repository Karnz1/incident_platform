from fastapi import FastAPI
from typing import List
from contextlib import asynccontextmanager
from .routes import incident_router
from .db import init_pg_pool, close_pg_pool, init_redis, close_redis



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pg_pool()
    await init_redis()

    yield

    await close_redis()
    await close_pg_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(incident_router)

