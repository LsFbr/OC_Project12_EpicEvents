import pytest

from tests.conftest import FakeSession, FakeUser

from epicevents.models.collaborator import Collaborator
from epicevents.models.role import Role
from epicevents.services.collaborators import (
    get_all_collaborators,
    create_collaborator,
    update_collaborator,
    delete_collaborator,
)


def raise_authentication_failed():
    raise Exception("Authentication failed")


def raise_no_user():
    raise Exception("User no longer exists")


def raise_no_permission(role, action):
    raise PermissionError("No permission")


def allow_authenticated_user(monkeypatch, user):
    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)


@pytest.fixture
def sales_role():
    return type("FakeRoleObj", (), {"id": 1, "name": "SALES"})()


@pytest.fixture
def support_role():
    return type("FakeRoleObj", (), {"id": 2, "name": "SUPPORT"})()


@pytest.fixture
def management_role():
    return type("FakeRoleObj", (), {"id": 3, "name": "MANAGEMENT"})()


@pytest.fixture
def collaborator_one(sales_role):
    user = FakeUser(
        user_id=101,
        employee_number=1,
        full_name="Collab One",
        email="collabone@example.com",
        role_name="SALES",
    )
    user.role_id = sales_role.id
    return user


@pytest.fixture
def collaborator_two(support_role):
    user = FakeUser(
        user_id=102,
        employee_number=2,
        full_name="Collab Two",
        email="collabtwo@example.com",
        role_name="SUPPORT",
    )
    user.role_id = support_role.id
    return user


@pytest.fixture
def collaborator_three(management_role):
    user = FakeUser(
        user_id=103,
        employee_number=3,
        full_name="Collab Three",
        email="collabthree@example.com",
        role_name="MANAGEMENT",
    )
    user.role_id = management_role.id
    return user


# -------------------------
# get_all_collaborators
# -------------------------

def test_get_all_collaborators_ok(monkeypatch, fake_user, collaborator_one, collaborator_two, collaborator_three):
    session = FakeSession(execute_items=[collaborator_one, collaborator_two, collaborator_three])

    allow_authenticated_user(monkeypatch, fake_user)

    collaborators = get_all_collaborators(session)

    assert len(collaborators) == 3
    assert collaborators[0].full_name == "Collab One"
    assert collaborators[1].full_name == "Collab Two"
    assert collaborators[2].full_name == "Collab Three"


def test_get_all_collaborators_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        get_all_collaborators(session)


def test_get_all_collaborators_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        get_all_collaborators(session)


def test_get_all_collaborators_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        get_all_collaborators(session)


def test_get_all_collaborators_no_collaborators(monkeypatch, fake_user):
    session = FakeSession(execute_items=[])

    allow_authenticated_user(monkeypatch, fake_user)

    collaborators = get_all_collaborators(session)

    assert collaborators == []


# -------------------------
# create_collaborator
# -------------------------

def test_create_collaborator_ok(monkeypatch, fake_user, sales_role):
    session = FakeSession(
        query_map={
            Role: [sales_role],
            Collaborator: [],
        }
    )

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    collaborator = create_collaborator(
        session=session,
        employee_number=4,
        full_name="  Collab Four  ",
        email="CollabFour@example.com",
        role_name="sales",
        plain_password="S3cretPwd!",
    )

    assert collaborator.id == 999
    assert collaborator.employee_number == 4
    assert collaborator.full_name == "Collab Four"
    assert collaborator.email == "collabfour@example.com"
    assert collaborator.password_hash == "hashed"
    assert collaborator.role_id == sales_role.id
    assert session.committed is True


def test_create_collaborator_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(Exception, match="Authentication failed"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(Exception, match="User no longer exists"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "hashed")

    with pytest.raises(PermissionError, match="No permission"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_missing_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number is required"):
        create_collaborator(session, None, "Collab", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_invalid_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number must be an integer"):
        create_collaborator(session, "bad", "Collab", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_missing_full_name(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="full_name is required"):
        create_collaborator(session, 4, "", "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_too_long_full_name(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="full_name must be less than 64 characters"):
        create_collaborator(session, 4, "A" * 65, "collab@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_missing_email(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email is required"):
        create_collaborator(session, 4, "Collab", "", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_invalid_email(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email is invalid"):
        create_collaborator(session, 4, "Collab", "not-an-email", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_too_long_email(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email must be less than 128 characters"):
        create_collaborator(session, 4, "Collab", "a" * 117 + "@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_missing_role_name(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="role_name is required"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "", "S3cretPwd!")


def test_create_collaborator_rejects_unknown_role(monkeypatch, fake_user):
    session = FakeSession(query_map={Role: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="unknown role"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "UNKNOWN", "S3cretPwd!")


def test_create_collaborator_rejects_duplicate_email(monkeypatch, fake_user, sales_role, collaborator_one):
    session = FakeSession(
        query_map={
            Role: [sales_role],
            Collaborator: [collaborator_one],
        }
    )

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email already exists"):
        create_collaborator(session, 4, "Collab", collaborator_one.email, "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_duplicate_employee_number(monkeypatch, fake_user, sales_role, collaborator_three):
    session = FakeSession(
        query_map={
            Role: [sales_role],
            Collaborator: [collaborator_three],
        }
    )

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number already exists"):
        create_collaborator(session, collaborator_three.employee_number, "Collab", "new@example.com", "SALES", "S3cretPwd!")


def test_create_collaborator_rejects_short_password(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="password too short"):
        create_collaborator(session, 4, "Collab", "collab@example.com", "SALES", "short")


# -------------------------
# update_collaborator
# -------------------------

def test_update_collaborator_ok(monkeypatch, fake_user, collaborator_one, support_role):
    session = FakeSession(
        query_map={
            Collaborator: [collaborator_one],
            Role: [support_role],
        }
    )

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.hash_password", lambda password: "new_hashed")

    collaborator = update_collaborator(
        session=session,
        employee_number=1,
        full_name=" Updated Collab One ",
        email="UpdatedOne@example.com",
        role_name="support",
        plain_password="NewS3cretPwd!",
    )

    assert collaborator.full_name == "Updated Collab One"
    assert collaborator.email == "updatedone@example.com"
    assert collaborator.role_id == support_role.id
    assert collaborator.password_hash == "new_hashed"
    assert session.committed is True


def test_update_collaborator_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        update_collaborator(session, 1, full_name="Updated")


def test_update_collaborator_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        update_collaborator(session, 1, full_name="Updated")


def test_update_collaborator_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        update_collaborator(session, 1, full_name="Updated")


def test_update_collaborator_rejects_missing_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number is required"):
        update_collaborator(session, None, full_name="Updated")


def test_update_collaborator_rejects_invalid_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number must be an integer"):
        update_collaborator(session, "bad", full_name="Updated")


def test_update_collaborator_rejects_no_fields(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="no fields to update"):
        update_collaborator(session, 1)


def test_update_collaborator_rejects_collaborator_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Collaborator: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="collaborator not found"):
        update_collaborator(session, 999, full_name="Updated")


def test_update_collaborator_rejects_missing_full_name(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="full_name is required"):
        update_collaborator(session, 1, full_name="")


def test_update_collaborator_rejects_too_long_full_name(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="full_name must be less than 64 characters"):
        update_collaborator(session, 1, full_name="A" * 65)


def test_update_collaborator_rejects_missing_email(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email is required"):
        update_collaborator(session, 1, email="")


def test_update_collaborator_rejects_invalid_email(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email is invalid"):
        update_collaborator(session, 1, email="not-an-email")


def test_update_collaborator_rejects_too_long_email(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email must be less than 128 characters"):
        update_collaborator(session, 1, email="a" * 117 + "@example.com")


def test_update_collaborator_rejects_existing_email(monkeypatch, fake_user, collaborator_one, collaborator_two):
    session = FakeSession(query_map={Collaborator: [collaborator_one, collaborator_two]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="email already exists"):
        update_collaborator(session, 1, email=collaborator_two.email)


def test_update_collaborator_rejects_missing_role_name(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="role_name is required"):
        update_collaborator(session, 1, role_name="")


def test_update_collaborator_rejects_unknown_role(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(
        query_map={
            Collaborator: [collaborator_one],
            Role: [],
        }
    )

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="unknown role"):
        update_collaborator(session, 1, role_name="UNKNOWN")


def test_update_collaborator_rejects_missing_password(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="password is required"):
        update_collaborator(session, 1, plain_password="")


def test_update_collaborator_rejects_short_password(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="password too short"):
        update_collaborator(session, 1, plain_password="short")


# -------------------------
# delete_collaborator
# -------------------------

def test_delete_collaborator_ok(monkeypatch, fake_user, collaborator_one):
    session = FakeSession(query_map={Collaborator: [collaborator_one]})

    allow_authenticated_user(monkeypatch, fake_user)

    collaborator = delete_collaborator(session, 1)

    assert collaborator == collaborator_one
    assert collaborator_one in session.deleted
    assert session.committed is True


def test_delete_collaborator_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        delete_collaborator(session, 1)


def test_delete_collaborator_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        delete_collaborator(session, 1)


def test_delete_collaborator_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.collaborators.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.collaborators.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.collaborators.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        delete_collaborator(session, 1)


def test_delete_collaborator_rejects_missing_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number is required"):
        delete_collaborator(session, None)


def test_delete_collaborator_rejects_invalid_employee_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="employee_number must be an integer"):
        delete_collaborator(session, "bad")


def test_delete_collaborator_rejects_collaborator_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Collaborator: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="collaborator not found"):
        delete_collaborator(session, 999)