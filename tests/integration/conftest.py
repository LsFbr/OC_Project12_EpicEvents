import os
from pathlib import Path

import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["EPICEVENTS_SECRET"] = "test-secret-test-secret-test-secret"

from epicevents.models.base import Base
from epicevents.models.role import Role
from epicevents.models.collaborator import Collaborator
from epicevents.security.passwords import hash_password


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def integration_env(tmp_path, monkeypatch):
    db_path = tmp_path / "integration_test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("epicevents.auth.current_user.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", TestingSessionLocal)

    session = TestingSessionLocal()
    try:
        management_role = Role(name="MANAGEMENT")
        sales_role = Role(name="SALES")
        support_role = Role(name="SUPPORT")
        session.add_all([management_role, sales_role, support_role])
        session.commit()

        management = Collaborator(
            employee_number=10,
            full_name="Management User",
            email="management@test.com",
            password_hash=hash_password("Password123"),
            role_id=management_role.id,
        )
        sales = Collaborator(
            employee_number=20,
            full_name="Sales User",
            email="sales@test.com",
            password_hash=hash_password("Password123"),
            role_id=sales_role.id,
        )
        support = Collaborator(
            employee_number=30,
            full_name="Support User",
            email="support@test.com",
            password_hash=hash_password("Password123"),
            role_id=support_role.id,
        )

        session.add_all([management, sales, support])
        session.commit()
    finally:
        session.close()

    return {
        "SessionLocal": TestingSessionLocal,
        "tmp_path": tmp_path,
    }