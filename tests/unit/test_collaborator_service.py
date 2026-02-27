import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from epicevents.models.base import Base
from epicevents.models.role import Role
from epicevents.services.collaborators import create_collaborator
from epicevents.security.passwords import verify_password


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


@pytest.fixture
def seeded_roles(session):
    session.add_all([Role(name="SALES"), Role(name="SUPPORT"), Role(name="MANAGEMENT")])
    session.commit()


def test_create_collaborator_ok(session, seeded_roles):
    collaborator = create_collaborator(
        session=session,
        employee_number="1001",
        full_name="Alice Doe",
        email="alice@example.com",
        role_name="SALES",
        plain_password="S3cretPwd!",
    )
    assert collaborator.id is not None
    assert collaborator.email == "alice@example.com"
    assert verify_password("S3cretPwd!", collaborator.password_hash) is True


def test_create_collaborator_rejects_duplicate_email(session, seeded_roles):
    create_collaborator(
        session=session,
        employee_number="1003",
        full_name="A",
        email="dup@example.com",
        role_name="SALES",
        plain_password="S3cretPwd!",
    )

    with pytest.raises(ValueError, match="email already exists"):
        create_collaborator(
            session=session,
            employee_number="1004",
            full_name="B",
            email="dup@example.com",
            role_name="SUPPORT",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_rejects_duplicate_employee_number(session, seeded_roles):
    create_collaborator(
        session=session,
        employee_number="1005",
        full_name="A",
        email="a@example.com",
        role_name="SALES",
        plain_password="S3cretPwd!",
    )

    with pytest.raises(ValueError, match="employee_number already exists"):
        create_collaborator(
            session=session,
            employee_number="1005",
            full_name="B",
            email="b@example.com",
            role_name="SUPPORT",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_invalid_employee_number(session, seeded_roles):
    with pytest.raises(ValueError, match="employee_number is required"):
        create_collaborator(
            session=session,
            employee_number="",
            full_name="Alice",
            email="alice@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )

def test_create_collaborator_with_invalid_full_name(session, seeded_roles):
    with pytest.raises(ValueError, match="full_name is required"):
        create_collaborator(
            session=session,
            employee_number="1006",
            full_name="",
            email="alice@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )

def test_create_collaborator_with_invalid_email(session, seeded_roles):
    with pytest.raises(ValueError, match="email is invalid"):
        create_collaborator(
            session=session,
            employee_number="1006",
            full_name="Alice",
            email="not-an-email",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )

def test_create_collaborator_with_too_short_password(session, seeded_roles):
    with pytest.raises(ValueError, match="password too short"):
        create_collaborator(
            session=session,
            employee_number="1006",
            full_name="Alice",
            email="alice@example.com",
            role_name="SALES",
            plain_password="short",
        )

def test_create_collaborator_with_invalid_role_name(session, seeded_roles):
    with pytest.raises(ValueError, match="unknown role"):
        create_collaborator(
            session=session,
            employee_number="1006",
            full_name="Alice",
            email="alice@example.com",
            role_name="UNKNOWN",
            plain_password="S3cretPwd!",
        )