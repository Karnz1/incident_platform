import os
from typing import AsyncGenerator
import redis.asyncio as redis
from dotenv import load_dotenv
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()

pg_pool: AsyncConnectionPool | None = None
redis_client: redis.Redis | None = None


def get_pg_conninfo() -> str:
    return (
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')} "
        f"host={os.getenv('PG_HOST')} "
        f"port={os.getenv('PG_PORT', '5432')}"
    )


async def init_pg_pool() -> None:
    global pg_pool

    pg_pool = AsyncConnectionPool(
        conninfo=get_pg_conninfo(),
        min_size=int(os.getenv("PG_POOL_MIN", "1")),
        max_size=int(os.getenv("PG_POOL_MAX", "10")),
        open=False,
        kwargs={
            "row_factory": dict_row,
        },
    )

    await pg_pool.open()
    await pg_pool.wait()

    return pg_pool

async def close_pg_pool() -> None:
    global pg_pool

    if pg_pool is not None:
        await pg_pool.close()
        pg_pool = None


async def get_pg_db() -> AsyncGenerator[AsyncConnection, None]:
    if pg_pool is None:
        raise RuntimeError("Postgres pool was not initialized")

    async with pg_pool.connection() as conn:
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise


async def init_redis() -> None:
    global redis_client

    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD") or None,
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
        max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
    )

    await redis_client.ping()
    return redis_client


async def close_redis() -> None:
    global redis_client

    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


def get_redis_client() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client was not initialized")

    return redis_client











####################

# import psycopg
# from dotenv import load_dotenv
# import os
# from contextlib import asynccontextmanager
# import redis.asyncio as redis

# # load environment variables
# load_dotenv()

# @asynccontextmanager
# async def get_pg_db():
#     conn_info = f'dbname={os.getenv("PG_DATABASE_NAME")} user={os.getenv("PG_USER")} password={os.getenv("PG_PASSWORD")} host={os.getenv("HOST")}'
#     async with await psycopg.AsyncConnection.connect(conn_info) as conn: 
#         try:
#             yield conn
#         finally:
#             print("closing connection")


# @asynccontextmanager           
# async def get_redis_db():
#     pool = redis.ConnectionPool(
#         host=os.getenv("HOST"),
#         port=os.getenv("RS_PORT"),
#         password=os.getenv("RS_PASSWORD"),
#         db=0,
#         decode_responses=True,
#         max_connections=10
#     )
#     client = redis.Redis(connection_pool=pool)
#     try:
#         yield client
#     finally:
#         await client.close()