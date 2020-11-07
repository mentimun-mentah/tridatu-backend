import pytest
from app import app
from httpx import AsyncClient
from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
async def async_client(client):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac
