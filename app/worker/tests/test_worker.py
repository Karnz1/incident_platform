"""
Unit tests for app.worker.

Run with:
    pytest -q tests/test_worker.py

These tests mock PostgreSQL, Redis, and the worker's DB lifecycle functions,
so no external services are required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.worker as worker


class FakeCursor:
    def __init__(self, row=None, rowcount: int = 1):
        self._row = row
        self.rowcount = rowcount

    async def fetchone(self):
        return self._row


class FakeConnection:
    def __init__(self, incident=None, update_rowcount: int = 1):
        self.incident = incident
        self.update_rowcount = update_rowcount
        self.execute_calls = []
        self.commit = AsyncMock()

    async def execute(self, sql, params):
        self.execute_calls.append((sql, params))
        if "SELECT id, title, description" in sql:
            return FakeCursor(row=self.incident)
        if "UPDATE incidents" in sql:
            return FakeCursor(rowcount=self.update_rowcount)
        raise AssertionError(f"Unexpected SQL executed: {sql}")


class FakeConnectionContext:
    def __init__(self, conn: FakeConnection):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePgPool:
    def __init__(self, conn: FakeConnection):
        self.conn = conn

    def connection(self):
        return FakeConnectionContext(self.conn)


@pytest.fixture(autouse=True)
def reset_shutdown_event():
    """Keep global worker state isolated between tests."""
    worker.shutdown_event.clear()
    yield
    worker.shutdown_event.clear()


def test_normalize_text_lowercases_collapses_whitespace_and_strips():
    assert worker.normalize_text("  System\n\tDOWN   Now  ") == "system down now"


@pytest.mark.parametrize(
    ("title", "description", "expected_severity", "expected_sla_hours"),
    [
        ("Production outage", "All users cannot access the app", "CRITICAL", 1),
        ("Checkout very slow", "Many users report timeout errors", "HIGH", 2),
        ("Profile bug", "Some users see incorrect data", "MEDIUM", 4),
        ("How to export report", "General question", "LOW", 6),
    ],
)
def test_determine_severity_and_sla_matches_keyword_rules(
    title, description, expected_severity, expected_sla_hours
):
    assert worker.determine_severity_and_sla(title, description) == (
        expected_severity,
        expected_sla_hours,
    )


def test_determine_severity_and_sla_uses_priority_order_for_multiple_matches():
    # CRITICAL should win even when the text also contains HIGH/MEDIUM/LOW keywords.
    assert worker.determine_severity_and_sla(
        "System down",
        "The service is very slow and users report errors",
    ) == ("CRITICAL", 1)


def test_determine_severity_and_sla_defaults_to_low_with_one_hour_sla():
    assert worker.determine_severity_and_sla("Hello", "Need assistance") == ("LOW", 1)


@pytest.mark.asyncio
async def test_fetch_incident_returns_database_row():
    row = {"id": 123, "title": "App down", "description": "All users affected"}
    conn = FakeConnection(incident=row)

    result = await worker.fetch_incident(conn, 123)

    assert result == row
    assert len(conn.execute_calls) == 1
    sql, params = conn.execute_calls[0]
    assert "FROM incidents" in sql
    assert params == (123,)


@pytest.mark.asyncio
async def test_update_incident_writes_processed_status_severity_sla_and_processed_at():
    conn = FakeConnection(update_rowcount=1)
    sla_deadline = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    await worker.update_incident(conn, incident_id=123, severity=4, sla_deadline=sla_deadline)

    assert len(conn.execute_calls) == 1
    sql, params = conn.execute_calls[0]
    assert "UPDATE incidents" in sql
    assert params[0] == "processed"
    assert params[1] == 4
    assert params[2] == sla_deadline
    assert isinstance(params[3], datetime)
    assert params[3].tzinfo == timezone.utc
    assert params[4] == 123


@pytest.mark.asyncio
async def test_update_incident_raises_when_no_single_row_was_updated():
    conn = FakeConnection(update_rowcount=0)

    with pytest.raises(RuntimeError, match="Expected to update 1 incident row"):
        await worker.update_incident(
            conn,
            incident_id=123,
            severity=1,
            sla_deadline=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
async def test_process_incident_updates_found_incident_and_commits(monkeypatch):
    # Keep the test independent of the real Severity enum implementation.
    monkeypatch.setattr(
        worker,
        "Severity",
        {
            "CRITICAL": SimpleNamespace(value=4),
            "HIGH": SimpleNamespace(value=3),
            "MEDIUM": SimpleNamespace(value=2),
            "LOW": SimpleNamespace(value=1),
        },
    )

    incident = {
        "id": 123,
        "title": "Payment failure",
        "description": "All users cannot pay",
    }
    conn = FakeConnection(incident=incident)
    pg_pool = FakePgPool(conn)

    before = datetime.now(timezone.utc)
    await worker.process_incident(123, pg_pool)
    after = datetime.now(timezone.utc)

    assert conn.commit.await_count == 1
    assert len(conn.execute_calls) == 2

    update_sql, update_params = conn.execute_calls[1]
    assert "UPDATE incidents" in update_sql
    assert update_params[0] == "processed"
    assert update_params[1] == 4
    assert before <= update_params[2] <= after + worker.timedelta(hours=2)
    assert update_params[4] == 123


@pytest.mark.asyncio
async def test_process_incident_does_nothing_when_incident_not_found():
    conn = FakeConnection(incident=None)
    pg_pool = FakePgPool(conn)

    await worker.process_incident(999, pg_pool)

    assert conn.commit.await_count == 0
    assert len(conn.execute_calls) == 1
    assert "SELECT id, title, description" in conn.execute_calls[0][0]


@pytest.mark.asyncio
async def test_worker_loop_skips_invalid_redis_id_and_cleans_up(monkeypatch):
    redis_client = AsyncMock()
    responses = [
        (worker.QUEUE_NAME, b"not-an-int"),
        None,
    ]

    monkeypatch.setattr(worker, "init_pg_pool", AsyncMock(return_value=object()))
    monkeypatch.setattr(worker, "init_redis", AsyncMock(return_value=redis_client))
    monkeypatch.setattr(worker, "close_redis", AsyncMock())
    monkeypatch.setattr(worker, "close_pg_pool", AsyncMock())
    process_incident = AsyncMock()
    monkeypatch.setattr(worker, "process_incident", process_incident)

    async def stop_after_first_sleep(_seconds):
        worker.shutdown_event.set()

    # Stop the loop after it observes one empty queue read.
    async def brpop_then_stop(*args, **kwargs):
        result = responses.pop(0)
        if result is None:
            worker.shutdown_event.set()
        return result

    redis_client.brpop.side_effect = brpop_then_stop
    monkeypatch.setattr(worker.asyncio, "sleep", stop_after_first_sleep)

    await worker.worker_loop()

    process_incident.assert_not_awaited()
    worker.close_redis.assert_awaited_once()
    worker.close_pg_pool.assert_awaited_once()


@pytest.mark.asyncio
async def test_worker_loop_processes_valid_redis_id_and_cleans_up(monkeypatch):
    redis_client = AsyncMock()

    async def brpop_once(*args, **kwargs):
        worker.shutdown_event.set()
        return (worker.QUEUE_NAME, b"123")

    redis_client.brpop.side_effect = brpop_once

    pg_pool = object()
    monkeypatch.setattr(worker, "init_pg_pool", AsyncMock(return_value=pg_pool))
    monkeypatch.setattr(worker, "init_redis", AsyncMock(return_value=redis_client))
    monkeypatch.setattr(worker, "close_redis", AsyncMock())
    monkeypatch.setattr(worker, "close_pg_pool", AsyncMock())
    process_incident = AsyncMock()
    monkeypatch.setattr(worker, "process_incident", process_incident)

    await worker.worker_loop()

    process_incident.assert_awaited_once_with(123, pg_pool)
    worker.close_redis.assert_awaited_once()
    worker.close_pg_pool.assert_awaited_once()
