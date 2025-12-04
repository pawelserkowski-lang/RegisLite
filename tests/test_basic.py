import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """Sprawdza czy pacjent oddycha."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "model" in data

def test_root_endpoint():
    """Sprawdza czy dashboard jest serwowany."""
    # Może zwrócić 200 (plik) lub JSON jeśli brak pliku, ale nie 500
    response = client.get("/")
    assert response.status_code == 200

def test_invalid_upload():
    """Sprawdza czy system odrzuca pliki nie-zip."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"nie jestem zipem", "text/plain")}
    )
    assert response.status_code == 400