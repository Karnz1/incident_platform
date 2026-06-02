def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_dependency_check_message(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == "dependencies check"


def test_metrics_endpoint_exists(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.json() == "return prometheus metrics"