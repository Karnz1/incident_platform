import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.db import get_pg_db, get_redis_client


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, query, params=None):
        self.conn.executed_queries.append(
            {
                "query": query,
                "params": params,
            }
        )

    async def fetchone(self):
        return self.conn.fetchone_result

    async def fetchall(self):
        return self.conn.fetchall_result


class FakePgConnection:
    def __init__(self):
        self.executed_queries = []
        self.fetchone_result = None
        self.fetchall_result = []
        self.commit_calls = 0
        self.rollback_calls = 0

    def cursor(self):
        return FakeCursor(self)

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1


class FakeRedis:
    def __init__(self):
        self.pushed_items = []

    async def rpush(self, queue_name, value):
        self.pushed_items.append(
            {
                "queue": queue_name,
                "value": value,
            }
        )
        return len(self.pushed_items)


@pytest.fixture
def fake_pg():
    return FakePgConnection()


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def client(fake_pg, fake_redis):
    async def override_pg_db():
        yield fake_pg

    def override_redis_client():
        return fake_redis

    app.dependency_overrides[get_pg_db] = override_pg_db
    app.dependency_overrides[get_redis_client] = override_redis_client

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()