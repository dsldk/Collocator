import pytest
from fastapi.testclient import TestClient
from os import environ

environ["ENABLE_SECURITY"] = "false"
environ["FASTAPI_SIMPLE_SECURITY_API_KEY_FILE"] = ""

from collocator import CONFIG
from collocator.app import app
from collocator.main import load_all_models


# @pytest.mark.asyncio
# async def test_load_all_models_returns_dict():
#    result = await load_all_models()
#    assert isinstance(result, dict)


class ASGITestClient(TestClient):
    """Test client that starts and stops the app on enter and exit."""

    async def __aenter__(self):
        await self.app.router.startup()  # type: ignore
        return super().__aenter__()  # type: ignore

    async def __aexit__(self, *args, **kwargs):
        await self.app.router.shutdown()  # type: ignore
        return await super().__aexit__(*args, **kwargs)  # type: ignore


@pytest.fixture(scope="module")
def test_client():
    with ASGITestClient(app) as client:
        yield client


client = TestClient(app)


model_info_keys = [
    ("delimiter", str),
    ("min_count", int),
    ("threshold", float),
    ("size", int),
    ("scorer", str),
]


def test_available_models(test_client: TestClient) -> None:
    response = test_client.get("/models")
    assert response.status_code == 200

    assert isinstance(response.json(), dict)
    assert len(response.json()) == len(CONFIG.get("general", "models").split(","))

    model = response.json().get("infomedia")
    assert isinstance(model, dict)
    assert model.get("title") == "Infomedia"

    for key, klass in model_info_keys:
        assert key in model.keys()
        assert isinstance(model.get(key), klass)


def test_search_endpoint(test_client: TestClient) -> None:
    response = test_client.get("/search/infomedia/hus")
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)

    keys = ["word", "threshold", "ngrams", "included_forms", "model_info"]
    for key in keys:
        assert key in result

    ngrams = result.get("ngrams", {})
    ngram_keys = ["left", "right", "in"]
    for key in ngram_keys:
        assert key in ngrams
        assert isinstance(ngrams.get(key), list)
        if len(ngrams.get(key, [])) > 0:
            assert isinstance(ngrams.get(key, [])[0], list)
            assert len(ngrams.get(key, [])[0]) == 2
            assert isinstance(ngrams.get(key, [])[0][0], str)
            assert isinstance(ngrams.get(key, [])[0][1], float)

    model_info = result.get("model_info", {})
    for key, klass in model_info_keys:
        assert key in model_info.keys()
        assert isinstance(model_info[key], klass)
