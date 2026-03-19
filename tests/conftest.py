import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from epicevents.models.base import Base
from epicevents.db.session import SessionLocal
from pathlib import Path

# Set the JWT secret key for the tests
os.environ["EPICEVENTS_SECRET"] = "test-secret-test-secret-test-secret"

@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()   


class FakeRole:
    def __init__(self, name="fake_role"):
        self.name = name


class FakeUser:
    def __init__(self, user_id=1, role="fake_role"):
        self.id = user_id
        self.role = FakeRole(role)
        self.email = "test@test.com"
        self.password_hash = "hashed"


class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self.user

    def options(self, *args):
        return self


class FakeSession:
    def __init__(self, user):
        self.user = user

    def query(self, model):
        return FakeQuery(self.user)

    def close(self):
        pass


@pytest.fixture
def fake_session():
    return FakeSession(FakeUser(1))

@pytest.fixture
def fake_user():
    return FakeUser(1)

@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """
    Replace Path.home() with a temporary directory.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path