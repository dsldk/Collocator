"""Testing the service."""
from fastapi.testclient import TestClient
from os import environ

environ["ENABLE_SECURITY"] = "false"
environ["FASTAPI_SIMPLE_SECURITY_API_KEY_FILE"] = ""

from collocator.app import app

client = TestClient(app)


def test_health() -> None:
    """Test healthcheck."""
    response = client.get("/health")
    assert response.status_code == 200
