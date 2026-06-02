from api.routes.incidents import (
    INCIDENT_REVIEW_QUEUE,
    severity_int_to_color,
    severity_int_to_name,
)


def test_severity_int_to_name_returns_enum_name():
    assert severity_int_to_name(1) == "CRITICAL"
    assert severity_int_to_name(2) == "HIGH"
    assert severity_int_to_name(3) == "MEDIUM"
    assert severity_int_to_name(4) == "LOW"


def test_severity_int_to_name_returns_none_for_unknown_value():
    assert severity_int_to_name(999) is None
    assert severity_int_to_name(None) is None


def test_severity_int_to_color_returns_expected_color():
    assert severity_int_to_color(1) == "#ef4444"
    assert severity_int_to_color(2) == "#f97316"
    assert severity_int_to_color(3) == "#eab308"
    assert severity_int_to_color(4) == "#22c55e"


def test_severity_int_to_color_returns_default_for_unknown_value():
    assert severity_int_to_color(999) == "#6b7280"
    assert severity_int_to_color(None) == "#6b7280"


def test_create_incident_inserts_to_db_and_pushes_to_redis(client, fake_pg, fake_redis):
    fake_pg.fetchone_result = {"id": 123}

    payload = {
        "title": "Database outage",
        "description": "Production database is not responding",
    }

    response = client.post("/incidents", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": 123,
        "status": "queued",
    }

    assert len(fake_pg.executed_queries) == 1

    executed = fake_pg.executed_queries[0]

    assert "INSERT INTO incidents" in executed["query"]
    assert executed["params"] == (
        "Database outage",
        "Production database is not responding",
        "queued",
    )

    # create_incident currently commits explicitly.
    assert fake_pg.commit_calls == 0

    assert fake_redis.pushed_items == [
        {
            "queue": INCIDENT_REVIEW_QUEUE,
            "value": "123",
        }
    ]


def test_create_incident_rejects_short_title(client):
    payload = {
        "title": "DB",
        "description": "Production database is not responding",
    }

    response = client.post("/incidents", json=payload)

    assert response.status_code == 422


def test_create_incident_rejects_short_description(client):
    payload = {
        "title": "Database outage",
        "description": "no",
    }

    response = client.post("/incidents", json=payload)

    assert response.status_code == 422


def test_get_all_incidents_returns_rows_with_severity_names_and_colors(client, fake_pg):
    fake_pg.fetchall_result = [
        {
            "id": 2,
            "title": "API latency",
            "description": "API response time is high",
            "status": "processed",
            "severity": 2,
            "sla_deadline": None,
            "processed_at": None,
        },
        {
            "id": 1,
            "title": "Minor UI bug",
            "description": "Button alignment is broken",
            "status": "processed",
            "severity": 4,
            "sla_deadline": None,
            "processed_at": None,
        },
        {
            "id": 0,
            "title": "Unknown severity",
            "description": "Severity value is invalid",
            "status": "processed",
            "severity": 999,
            "sla_deadline": None,
            "processed_at": None,
        },
    ]

    response = client.get("/incidents")

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 2,
            "title": "API latency",
            "description": "API response time is high",
            "status": "processed",
            "severity": "HIGH",
            "severity_color": "#f97316",
            "sla_deadline": None,
            "processed_at": None,
        },
        {
            "id": 1,
            "title": "Minor UI bug",
            "description": "Button alignment is broken",
            "status": "processed",
            "severity": "LOW",
            "severity_color": "#22c55e",
            "sla_deadline": None,
            "processed_at": None,
        },
        {
            "id": 0,
            "title": "Unknown severity",
            "description": "Severity value is invalid",
            "status": "processed",
            "severity": None,
            "severity_color": "#6b7280",
            "sla_deadline": None,
            "processed_at": None,
        },
    ]

    assert len(fake_pg.executed_queries) == 1
    assert "SELECT id, title, description, status, severity" in fake_pg.executed_queries[0]["query"]


def test_delete_incident_deletes_existing_incident(client, fake_pg):
    fake_pg.fetchone_result = {"id": 10}

    response = client.delete("/incidents/10")

    assert response.status_code == 200
    assert response.json() == {"id": 10}

    assert len(fake_pg.executed_queries) == 1

    executed = fake_pg.executed_queries[0]

    assert "DELETE FROM incidents WHERE id = %s RETURNING id" in executed["query"]
    assert executed["params"] == (10,)
    assert fake_pg.commit_calls == 1


def test_delete_incident_returns_404_when_incident_does_not_exist(client, fake_pg):
    fake_pg.fetchone_result = None

    response = client.delete("/incidents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Incident not found"}

    assert len(fake_pg.executed_queries) == 1
    assert fake_pg.commit_calls == 0