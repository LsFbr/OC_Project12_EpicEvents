import pytest

from epicevents.models.role import Role
from epicevents.services.collaborators import get_all_collaborators, create_collaborator, update_collaborator, delete_collaborator
from epicevents.models.collaborator import Collaborator


@pytest.fixture
def seeded_roles(session):
    session.add_all([Role(name="SALES"), Role(name="SUPPORT"), Role(name="MANAGEMENT")])
    session.commit()

@pytest.fixture
def seeded_collaborators(session):
    session.add_all([
        Collaborator(employee_number="1", full_name="Collab one", email="collabone@example.com", role_id=1, password_hash="hashed"),
        Collaborator(employee_number="2", full_name="Collab two", email="collabtwo@example.com", role_id=2, password_hash="hashed"),
        Collaborator(employee_number="3", full_name="Collab three", email="collabthree@example.com", role_id=3, password_hash="hashed"),
    ])
    session.commit()

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_user():
    raise Exception("User no longer exists")

def raise_no_permission(role, action):
    raise Exception("No permission")


# get_all_collaborators tests
def test_get_all_collaborators_ok(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    

    collaborators = get_all_collaborators(session)
    assert len(collaborators) == 3
    assert collaborators[0].full_name == "Collab one"
    assert collaborators[1].full_name == "Collab two"
    assert collaborators[2].full_name == "Collab three"


def test_get_all_collaborators_authentication_failed(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    with pytest.raises(Exception, match="Authentication failed"):
        get_all_collaborators(session)


def test_get_all_collaborators_no_user(session, seeded_collaborators, monkeypatch):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    with pytest.raises(Exception, match="User no longer exists"):
        get_all_collaborators(session)


def test_get_all_collaborators_no_permission(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)
    with pytest.raises(Exception, match="No permission"):
        get_all_collaborators(session)
        

def test_get_all_collaborators_no_collaborators(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    collaborators = get_all_collaborators(session)
    assert len(collaborators) == 0


# create_collaborator tests
def test_create_collaborator_ok(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")
    

    collaborator = create_collaborator(
        session=session,
        employee_number=4,
        full_name="Collab four",
        email="CollabFour@example.com",
        role_name="SALES",
        plain_password="S3cretPwd!",
    )
    assert collaborator.id is not None
    assert collaborator.email == "CollabFour@example.com".lower()
    assert collaborator.password_hash == "hashed"


def test_create_collaborator_rejects_duplicate_email(session, seeded_roles, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="email already exists"):
        create_collaborator(
            session=session,
            employee_number=1004,
            full_name="Collab four",
            email="CollabThree@example.com",
            role_name="SUPPORT",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_rejects_duplicate_employee_number(session, seeded_roles, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="employee_number already exists"):
        create_collaborator(
            session=session,
            employee_number=3,
            full_name="Collab",
            email="Collab@example.com",
            role_name="SUPPORT",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_no_employee_number(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="employee_number is required"):
        create_collaborator(
            session=session,
            employee_number=None,
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_invalid_employee_number(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="employee_number must be an integer"):
        create_collaborator(
            session=session,
            employee_number="not-an-integer",
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_no_full_name(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="full_name is required"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_too_long_full_name(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="full_name must be less than 64 characters"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="A" * 65,
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_no_email(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="email is required"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_invalid_email(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="email is invalid"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="not-an-email",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_too_long_email(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="email must be less than 128 characters"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="a" * 117 + "@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_no_role_name(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="role_name is required"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_with_invalid_role_name(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="unknown role"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="UNKNOWN",
            plain_password="S3cretPwd!",
        )

def test_create_collaborator_with_too_short_password(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(ValueError, match="password too short"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="short",
        )





def test_create_collaborator_authentication_failed(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(Exception, match="Authentication failed"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_no_user(session, seeded_roles, monkeypatch):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(Exception, match="User no longer exists"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


def test_create_collaborator_no_permission(session, seeded_roles, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(Exception, match="No permission"):
        create_collaborator(
            session=session,
            employee_number=4,
            full_name="Collab",
            email="collab@example.com",
            role_name="SALES",
            plain_password="S3cretPwd!",
        )


# update_collaborator tests
def test_update_collaborator_ok(session, seeded_roles, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed_updated")

    collaborator_to_update = session.query(Collaborator).filter(Collaborator.employee_number == 1).one()
    
    collaborator_updated = update_collaborator(
        session=session,
        employee_number=1,
        full_name="Collab one updated",
        email="collaboneupdated@example.com",
        role_name="SUPPORT",
        plain_password="S3cretPwd!updated",
    )
    assert collaborator_updated.id == collaborator_to_update.id
    assert collaborator_updated.full_name == "Collab one updated"
    assert collaborator_updated.email == "collaboneupdated@example.com".lower()
    assert collaborator_updated.role_id == 2
    assert collaborator_updated.password_hash == "hashed_updated"


def test_update_collaborator_authentication_failed(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    
    with pytest.raises(Exception, match="Authentication failed"):
        update_collaborator(
            session=session,
            employee_number=1,
            full_name="Collab one updated",
        )


def test_update_collaborator_no_user(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        update_collaborator(
            session=session,
            employee_number=1,
            full_name="Collab one updated",
        )


def test_update_collaborator_no_permission(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        update_collaborator(
            session=session,
            employee_number=1,
            full_name="Collab one updated",
        )


def test_update_collaborator_no_employee_number(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="employee_number is required"):
        update_collaborator(
            session=session,
            employee_number=None,
            full_name="Collab one updated",
        )


def test_update_collaborator_invalid_employee_number(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="employee_number must be an integer"):
        update_collaborator(
            session=session,
            employee_number="not-an-integer",
            full_name="Collab one updated",
        )


def test_update_collaborator_rejects_no_fields(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="no fields to update"):
        update_collaborator(
            session=session,
            employee_number=1,
        )


def test_update_collaborator_rejects_collaborator_not_found(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="collaborator not found"):
        update_collaborator(
            session=session,
            employee_number=100,
            full_name="Collab one updated",
        )


def test_update_collaborator_rejects_no_full_name(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="full_name is required"):
        update_collaborator(
            session=session,
            employee_number=1,
            full_name="",
        )


def test_update_collaborator_rejects_too_long_full_name(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="full_name must be less than 64 characters"):
        update_collaborator(
            session=session,
            employee_number=1,
            full_name="A" * 65,
        )


def test_update_collaborator_rejects_no_email(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is required"):
        update_collaborator(
            session=session,
            employee_number=1,
            email="",
        )


def test_update_collaborator_rejects_invalid_email(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is invalid"):
        update_collaborator(
            session=session,
            employee_number=1,
            email="not-an-email",
        )


def test_update_collaborator_rejects_too_long_email(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email must be less than 128 characters"):
        update_collaborator(
            session=session,
            employee_number=1,
            email="a" * 117 + "@example.com",
        )


def test_update_collaborator_rejects_existing_email(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email already exists"):
        update_collaborator(
            session=session,
            employee_number=1,
            email="collabtwo@example.com"
        )


def test_update_collaborator_rejects_no_role_name(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="role_name is required"):
        update_collaborator(
            session=session,
            employee_number=1,
            role_name="",
        )


def test_update_collaborator_rejects_invalid_role_name(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="unknown role"):
        update_collaborator(
            session=session,
            employee_number=1,
            role_name="UNKNOWN",
        )


def test_update_collaborator_rejects_no_password(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="password is required"):
        update_collaborator(
            session=session,
            employee_number=1,
            plain_password="",
        )
        

def test_update_collaborator_rejects_too_short_password(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="password too short"):
        update_collaborator(
            session=session,
            employee_number=1,
            plain_password="short",
        )


# delete_collaborator tests
def test_delete_collaborator_ok(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    delete_collaborator(
        session=session,
        employee_number=1,
    )

    collaborator = (
        session.query(Collaborator)
        .filter(Collaborator.employee_number == 1)
        .one_or_none()
    )
    assert collaborator is None


def test_delete_collaborator_authentication_failed(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        delete_collaborator(
            session=session,
            employee_number=1,
        )


def test_delete_collaborator_no_user(session, seeded_collaborators, monkeypatch):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        delete_collaborator(
            session=session,
            employee_number=1,
        )


def test_delete_collaborator_no_permission(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        delete_collaborator(
            session=session,
            employee_number=1,
        )


def test_delete_collaborator_rejects_missing_employee_number(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="employee_number is required"):
        delete_collaborator(
            session=session,
            employee_number=None,
        )


def test_delete_collaborator_rejects_collaborator_not_found(session, seeded_collaborators, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="collaborator not found"):
        delete_collaborator(
            session=session,
            employee_number=999,
        )