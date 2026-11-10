import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app

TEST_DB_NAME = "tracker_db_test"

_base_url = make_url(settings.database_url)
_admin_url = _base_url.set(drivername="postgresql", database="postgres")
_test_url = _base_url.set(database=TEST_DB_NAME)


@pytest.fixture(scope="session")
def _test_database():
    from psycopg import connect as pg_connect

    conninfo = _admin_url.render_as_string(hide_password=False)
    with pg_connect(conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    yield
    with pg_connect(conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')


@pytest.fixture(scope="session")
def _engine(_test_database):
    engine = create_engine(_test_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(_engine):
    TestingSession = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    with _engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE tasks, users RESTART IDENTITY CASCADE"))
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    client.post(
        "/auth/register",
        json={"email": "tester@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "tester@example.com", "password": "secret123"},
    )
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client