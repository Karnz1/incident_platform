from fastapi import FastAPI
from typing import List
from contextlib import asynccontextmanager
from .routes import incident_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to databases
    # (e.g., engine.connect() or verifying Redis ping)
    yield
    # Shutdown: Clean up connections
    #await engine.dispose()
    #await redis_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(incident_router)

