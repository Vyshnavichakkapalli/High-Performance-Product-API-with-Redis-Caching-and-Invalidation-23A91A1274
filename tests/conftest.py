import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from src.main import app
from src.db import get_session
from src.services.redis_service import redis_service
import redis

# Use in-memory SQLite for tests
DATABASE_URL = "sqlite://"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="redis_client")
def redis_fixture():
    """Connect to the actual Redis service for integration tests."""
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        r.flushdb()
        yield r
        r.flushdb()
    except redis.ConnectionError:
        pytest.skip("Redis not available")
