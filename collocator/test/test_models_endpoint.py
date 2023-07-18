import pytest
from fastapi.testclient import TestClient

from collocator import CONFIG
from collocator.app import app
from collocator.main import load_all_models


@pytest.mark.asyncio
async def test_load_all_models_returns_dict():
    result = await load_all_models()
    assert isinstance(result, dict)


client = TestClient(app)


def test_available_models() -> None:
    response = client.get("/models")
    assert response.status_code == 200
