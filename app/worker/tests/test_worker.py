"""Unit tests for the incident worker service.

These tests deliberately avoid real Postgres and Redis connections.

They also avoid assuming that `app.worker` always resolves to the worker module.
In some layouts, `app.worker` is a package directory, while the worker code lives in
another worker.py file or package __init__.py. The resolver below imports the module
that actually contains the worker functions under test.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "app").exists():
            return parent
    return current.parents[0]


PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _module_has_worker_api(module) -> bool:
    required = (
        "normalize_text",
        "determine_severity_and_sla",
        "fetch_incident",
        "update_incident",
        "process_incident",
        "worker_loop",
        "shutdown_event",
    )
    return all(hasattr(module, name) for name in required)


def _load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location("incident_worker_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not build import spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _import_worker_module():
    """Import the actual worker implementation, not an empty app.worker package."""

    try:
        module = importlib.import_module("app.worker")
        if _module_has_worker_api(module):
            return module
    except Exception:
        pass

    candidates = [
        PROJECT_ROOT / "app" / "worker.py",
        PROJECT_ROOT / "app" / "worker" / "__init__.py",
    ]

    app_dir = PROJECT_ROOT / "app"
    if app_dir.exists():
        candidates.extend(app_dir.rglob("*.py"))

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen or not candidate.exists():
            continue
        seen.add(candidate)

        if "tests" in candidate.parts:
            continue

        try:
            source = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if "def normalize_text" not in source:
            continue
        if "shutdown_event" not in source:
            continue
        if "def worker_loop" not in source:
            continue

        module = _load_module_from_path(candidate)
        if _module_has_worker_api(module):
            return module

    raise ImportError(
        "Could not find the worker implementation. Expected a module containing "
        "normalize_text, determine_severity_and_sla, worker_loop, and shutdown_event. "
        "Check whether the worker code is in app/worker.py or app/worker/__init__.py."
    )


worker = _import_worker_module()


class FakeCursor:
    def __init__(self, row=None, rowcount=1):
        self._row = row
        self.rowcount = rowcount

    async def fetchone(self):
        return self._row


class FakeConnection:
    def __init__(self, row=None, rowcount=1):
        self.row = row
        self.rowcount = rowcount
        self.executed_sql = None
        self.executed_params = None
        self.commit = AsyncMock()

    async def execute(self, sql, params):
        self.executed_sql = sql
        self.executed_params = params
        return FakeCursor(row=self.row, rowcount=self.rowcount)


class FakeConnectionContext:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self, conn):
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
    assert worker.normalize_text("  SYSTEM   DOWN\nNow\t ") == "system down now"


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
    title,
    description,
    expected_severity,
    expected_sla_hours,
):
    assert worker.determine_severity_and_sla(title, description) == (
        expected_severity,
        expected_sla_hours,
    )


def test_determine_severity_and_sla_uses_priority_order_for_multiple_matches():
    severity, sla_hours = worker.determine_severity_and_sla(
        "Question",
        "The production system is down and also slow",
    )

    assert severity == "CRITICAL"
    assert sla_hours == 1


def test_determine_severity_and_sla_defaults_to_low_with_one_hour_sla():
    assert worker.determine_severity_and_sla("Hello", "No matching words") == ("LOW", 1)


@pytest.mark.asyncio
async def test_fetch_incident_returns_database_row():
    row = {"id": 123, "title": "Outage", "description": "Service down"}
    conn = FakeConnection(row=row)

    result = await worker.fetch_incident(conn, 123)

    assert result == row
    assert "SELECT id, title, description" in conn.executed_sql
    assert conn.executed_params == (123,)


@pytest.mark.asyncio
async def test_update_incident_writes_processed_status_severity_sla_and_processed_at():
    conn = FakeConnection(rowcount=1)
    sla_deadline = datetime(2026, 1, 1, tzinfo=timezone.utc)

    await worker.update_incident(
        conn=conn,
        incident_id=42,
        severity=3,
        sla_deadline=sla_deadline,
    )

    assert "UPDATE incidents" in conn.executed_sql
    assert conn.executed_params[0] == "processed"
    assert conn.executed_params[1] == 3
    assert conn.executed_params[2] == sla_deadline
    assert isinstance(conn.executed_params[3], datetime)
    assert conn.executed_params[3].tzinfo == timezone.utc
    assert conn.executed_params[4] == 42


@pytest.mark.asyncio
async def test_update_incident_raises_when_no_single_row_was_updated():
    conn = FakeConnection(rowcount=0)

    with pytest.raises(RuntimeError, match="Expected to update 1 incident row"):
        await worker.update_incident(
            conn=conn,
            incident_id=42,
            severity=3,
            sla_deadline=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


@pytest.mark.asyncio
async def test_process_incident_updates_found_incident_and_commits(monkeypatch):
    row = {
        "id": 7,
        "title": "Production outage",
        "description": "All users cannot access checkout",
    }
    conn = FakeConnection(row=row)
    pool = FakePool(conn)

    update_mock = AsyncMock()
    monkeypatch.setattr(worker, "update_incident", update_mock)

    await worker.process_incident(7, pool)

    update_mock.assert_awaited_once()
    kwargs = update_mock.await_args.kwargs
    assert kwargs["conn"] is conn
    assert kwargs["incident_id"] == 7

    expected_severity_value = worker.Severity["CRITICAL"].value
    assert kwargs["severity"] == expected_severity_value
    assert kwargs["sla_deadline"].tzinfo == timezone.utc
    conn.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_incident_does_nothing_when_incident_not_found(monkeypatch):
    conn = FakeConnection(row=None)
    pool = FakePool(conn)

    update_mock = AsyncMock()
    monkeypatch.setattr(worker, "update_incident", update_mock)

    await worker.process_incident(999, pool)

    update_mock.assert_not_awaited()
    conn.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_worker_loop_skips_invalid_redis_id_and_cleans_up(monkeypatch):
    class FakeRedis:
        async def brpop(self, queue_name, timeout):
            worker.shutdown_event.set()
            return (queue_name, b"not-an-int")

    redis_client = FakeRedis()

    monkeypatch.setattr(worker, "init_pg_pool", AsyncMock(return_value=SimpleNamespace()))
    monkeypatch.setattr(worker, "init_redis", AsyncMock(return_value=redis_client))
    monkeypatch.setattr(worker, "close_redis", AsyncMock())
    monkeypatch.setattr(worker, "close_pg_pool", AsyncMock())

    process_mock = AsyncMock()
    monkeypatch.setattr(worker, "process_incident", process_mock)

    await worker.worker_loop()

    process_mock.assert_not_awaited()
    worker.close_redis.assert_awaited_once()
    worker.close_pg_pool.assert_awaited_once()


@pytest.mark.asyncio
async def test_worker_loop_processes_valid_redis_id_and_cleans_up(monkeypatch):
    pg_pool = SimpleNamespace()

    class FakeRedis:
        async def brpop(self, queue_name, timeout):
            worker.shutdown_event.set()
            return (queue_name, b"123")

    redis_client = FakeRedis()

    monkeypatch.setattr(worker, "init_pg_pool", AsyncMock(return_value=pg_pool))
    monkeypatch.setattr(worker, "init_redis", AsyncMock(return_value=redis_client))
    monkeypatch.setattr(worker, "close_redis", AsyncMock())
    monkeypatch.setattr(worker, "close_pg_pool", AsyncMock())

    process_mock = AsyncMock()
    monkeypatch.setattr(worker, "process_incident", process_mock)

    await worker.worker_loop()

    process_mock.assert_awaited_once_with(123, pg_pool)
    worker.close_redis.assert_awaited_once()
    worker.close_pg_pool.assert_awaited_once()
