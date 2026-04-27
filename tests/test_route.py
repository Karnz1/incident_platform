from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/health")

    assert response.status_code == 200


def test_health_check_response_body():
    response = client.get("/health")

    assert response.json() == {"status": "ok"}


def test_ready_returns_200():
    response = client.get("/ready")

    assert response.status_code == 200


def test_ready_response_body():
    response = client.get("/ready")

    assert response.json() == "dependencies check"


def test_metrics_returns_200():
    response = client.get("/metrics")

    assert response.status_code == 200


def test_metrics_response_body():
    response = client.get("/metrics")

    assert response.json() == "return prometheus metrics"