from fastapi.testclient import TestClient

from collocator.app import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "200"
