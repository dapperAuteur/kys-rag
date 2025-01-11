import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from app.core.database import database, Collection
import os
from app.core.config import get_settings

# Set test environment
os.environ["ENV"] = "test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def initialized_app():
    """Initialize app and database."""
    await database.connect()
    yield app
    await database.disconnect()

@pytest.fixture(scope="function")
def client(initialized_app) -> Generator:
    """Create a TestClient instance."""
    with TestClient(initialized_app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def async_client(initialized_app) -> AsyncGenerator:
    """Create an AsyncClient instance."""
    async with AsyncClient(
        base_url="http://testserver",
        app=initialized_app,
        backend='asyncio'
    ) as ac:
        yield ac

@pytest.fixture(autouse=True)
async def clean_database():
    """Clean database before and after each test."""
    settings = get_settings()
    if settings.ENV != "test":
        raise ValueError("Attempting to clean non-test database!")
    
    # Ensure we're connected and clean before test
    await database.connect()
    if database.is_connected:
        collections_to_clean = [
            Collection.SCIENTIFIC_STUDIES,
            Collection.ARTICLES,
            Collection.CHAT_HISTORY
        ]
        for collection in collections_to_clean:
            coll = await database.get_collection(collection)
            await coll.delete_many({})
    
    yield
    
    # Clean after test
    if database.is_connected:
        for collection in collections_to_clean:
            coll = await database.get_collection(collection)
            await coll.delete_many({})