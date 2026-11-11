from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_healt():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_add():
    response = client.post(
        "/calculate",
        json={
            "a": 10,
            "b": 5,
            "operation": "add"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": 15.0}

def test_subtract():
    response = client.post(
        "/calculate",
        json={
            "a": 10,
            "b": 5,
            "operation": "subtract"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}

def test_multiply():
    response = client.post(
        "/calculate",
        json={
            "a": 10,
            "b": 8,
            "operation": "multiply"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": 80}

def test_divide():
    response = client.post(
        "/calculate",
        json={
            "a": 100,
            "b": 5,
            "operation": "divide"
        }    
    )
    assert response.status_code == 200
    assert response.json() == {"result": 20.0}

def test_invalid_operation():
    response = client.post(
        "/calculate",
        json={
            "a": 10,
            "b": 5,
            "operation": "power"
        }
    )

    assert response.status_code == 422