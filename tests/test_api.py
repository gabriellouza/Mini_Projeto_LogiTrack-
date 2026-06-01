from fastapi.testclient import TestClient
from src.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_recalculate_route():
    payload = {
        "delivery_id": "ENT-1001",
        "origin": "Centro de Distribuição",
        "destination": "Cliente A",
        "priority": "media",
    }
    response = client.post("/routes/recalculate", json=payload)
    assert response.status_code == 200
    assert response.json()["delivery_id"] == "ENT-1001"
