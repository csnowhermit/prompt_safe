import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.api import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_chat_endpoint(client):
    response = await client.post(
        "/api/v1/chat",
        json={"prompt": "请帮我写一首关于春天的诗"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert "response" in data["data"]


@pytest.mark.asyncio
async def test_chat_empty_prompt(client):
    response = await client.post(
        "/api/v1/chat",
        json={"prompt": ""}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_mask_preview_endpoint(client):
    response = await client.post(
        "/api/v1/mask/preview",
        json={"text": "手机号13812345678，身份证110101199001011234"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data


@pytest.mark.asyncio
async def test_check_preview_endpoint(client):
    response = await client.post(
        "/api/v1/check/preview",
        json={"text": "请帮我写一首诗"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data