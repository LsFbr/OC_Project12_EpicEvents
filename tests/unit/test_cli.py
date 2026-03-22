import pytest

from epicevents.cli import cli as cli_module
from conftest import FakeUser


# tests login_command
def test_login_command_success(monkeypatch):
    echoed = []
    called = {}

    def fake_login(email, password):
        called["email"] = email
        called["password"] = password
        return "fake-token"

    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda label: "user@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda label: "Password123")

    monkeypatch.setattr("epicevents.cli.cli.login", fake_login)
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message: echoed.append(message))

    cli_module.login_command.callback()

    assert called == {"email": "user@example.com", "password": "Password123"}
    assert echoed == [("Login successful")]


def test_login_command_failure(monkeypatch):
    echoed = []

    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda label: "user@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda label: "Password123")

    def fake_login(email, password):
        raise Exception("Invalid email or password")

    monkeypatch.setattr("epicevents.cli.cli.login", fake_login)
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    cli_module.login_command.callback()

    assert echoed == [("Login failed: Invalid email or password", True)]


# tests logout_command
def test_logout_command_success(monkeypatch):
    echoed = []

    monkeypatch.setattr("epicevents.cli.cli.logout", lambda: None)
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message: echoed.append((message)),
    )

    cli_module.logout_command.callback()

    assert echoed == [("Logout successful")]


def test_logout_command_failure(monkeypatch):
    echoed = []

    def fake_logout():
        raise Exception("You were not logged in")

    monkeypatch.setattr("epicevents.cli.cli.logout", fake_logout)
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    cli_module.logout_command.callback()

    assert echoed == [("Logout failed: You were not logged in", True)]


# tests collaborators_list_command
def test_collaborators_list_command_success(monkeypatch, fake_session):
    echoed = []

    collaborator_1 = FakeUser(
        user_id=2,
        employee_number=1,
        full_name="User One",
        email="userone@example.com",
        role_name="MANAGEMENT",
    )
    collaborator_2 = FakeUser(
        user_id=3,
        employee_number=2,
        full_name="User Two",
        email="usertwo@example.com",
        role_name="SALES",
    )
    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_collaborators", lambda session: [collaborator_1, collaborator_2])
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message: echoed.append((message)))

    cli_module.collaborators_list_command.callback()

    assert echoed == [
        ("ID | Employee Number | Full Name | Email | Role"),
        ("--------------------------------------------------"),
        ("2 | 1 | User One | userone@example.com | MANAGEMENT"),
        ("3 | 2 | User Two | usertwo@example.com | SALES"),
    ]


def test_collaborators_list_command_no_collaborators(monkeypatch, fake_session):
    echoed = []

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_collaborators", lambda session: [])
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message: echoed.append((message)))

    cli_module.collaborators_list_command.callback()

    assert echoed == [("No collaborators found.")]


def test_collaborators_list_command_failure(monkeypatch, fake_session):
    echoed = []

    def fake_get_all_collaborators(session):
        raise Exception("Faillure Test")

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_collaborators", fake_get_all_collaborators)
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message, err=False: echoed.append((message, err)))

    cli_module.collaborators_list_command.callback()

    assert echoed == [("Collaborators list failed: Faillure Test", True)]


# tests collaborators_create_command
def test_collaborators_create_command_success(monkeypatch, fake_session):
    echoed = []

    collaborator = FakeUser(
        employee_number=4,
        full_name="Collab Four",
        email="collabfour@example.com",
        role_name="SALES",
    )

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda label, max_length: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda label: None)

    monkeypatch.setattr(
        "epicevents.cli.cli.create_collaborator",
        lambda session, employee_number, full_name, email, role, plain_password: collaborator,
    )
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message: echoed.append((message)),
    )

    cli_module.collaborators_create_command.callback()

    assert echoed == [
        ("Enter the details for the new collaborator (marked with * are required):"),
        ("Collaborator Collab Four created successfully."),
        ("ID | Employee Number | Full Name | Email | Role"),
        ("--------------------------------------------------"),
        ("1 | 4 | Collab Four | collabfour@example.com | SALES"),
    ]


def test_collaborators_create_command_failure(monkeypatch, fake_session):
    echoed = []

    def fake_create_collaborator(session, employee_number, full_name, email, role, plain_password):
        raise Exception("Faillure Test")

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda label, max_length: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.create_collaborator", fake_create_collaborator)
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message, err=False: echoed.append((message, err)),
    )

    cli_module.collaborators_create_command.callback()

    assert echoed == [
        ("Enter the details for the new collaborator (marked with * are required):", False),
        ("Collaborators create failed: Faillure Test", True),
    ]


# tests collaborators_update_command
def test_collaborators_update_command_success(monkeypatch, fake_session):
    echoed = []

    collaborator = FakeUser(
        user_id=1,
        employee_number=1,
        full_name="User One Updated",
        email="useroneupdated@example.com",
        role_name="SUPPORT",
    )

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: 1)
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_text",
        lambda label, required=False, max_length=64: "User One Updated",
    )
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_email",
        lambda label, required=False: "useroneupdated@example.com",
    )
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_role",
        lambda label, required=False: "SUPPORT",
    )
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_password",
        lambda label, required=False: "NewPassword123",
    )

    captured = {}

    def fake_update_collaborator(session, employee_number, **fields):
        captured["employee_number"] = employee_number
        captured["fields"] = fields
        return collaborator

    monkeypatch.setattr("epicevents.cli.cli.update_collaborator", fake_update_collaborator)
    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message, err=False: echoed.append((message, err)),
    )

    cli_module.collaborators_update_command.callback()

    assert captured["employee_number"] == 1
    assert captured["fields"] == {
        "full_name": "User One Updated",
        "email": "useroneupdated@example.com",
        "role_name": "SUPPORT",
        "plain_password": "NewPassword123",
    }
    assert echoed == [
        ("Enter the details for the collaborator to update (marked with * are required):", False),
        ("Collaborator User One Updated updated successfully.", False),
        ("ID | Employee Number | Full Name | Email | Role", False),
        ("--------------------------------------------------", False),
        ("1 | 1 | User One Updated | useroneupdated@example.com | SUPPORT", False),
    ]


def test_collaborators_update_command_failure(monkeypatch, fake_session):
    echoed = []

    def fake_update_collaborator(session, employee_number, **fields):
        raise Exception("Faillure Test")

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda label, required, max_length: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda label, required: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda label, required: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda label, required: None)
    
    monkeypatch.setattr("epicevents.cli.cli.update_collaborator", fake_update_collaborator)
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message, err=False: echoed.append((message, err)))

    cli_module.collaborators_update_command.callback()

    assert echoed == [
        ("Enter the details for the collaborator to update (marked with * are required):", False),
        ("Collaborators update failed: Faillure Test", True),
    ]


# tests collaborators_delete_command
def test_collaborators_delete_command_success(monkeypatch, fake_session):
    echoed = []

    collaborator = FakeUser(
        employee_number=1,
        full_name="User One",
        email="userone@example.com",
        role_name="MANAGEMENT",
    )

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: 1)
    monkeypatch.setattr("epicevents.cli.cli.delete_collaborator", lambda session, employee_number: collaborator)
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message: echoed.append((message)))

    cli_module.collaborators_delete_command.callback()

    assert echoed == [
        ("Enter the employee number of the collaborator to delete:"),
        ("Collaborator User One deleted successfully."),
    ]


def test_collaborators_delete_command_failure(monkeypatch, fake_session):
    echoed = []

    def fake_delete_collaborator(session, employee_number):
        raise Exception("Faillure Test")

    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: FakeUser(role_name="MANAGEMENT"))
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)

    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda label: None)
    monkeypatch.setattr("epicevents.cli.cli.delete_collaborator", fake_delete_collaborator)
    monkeypatch.setattr("epicevents.cli.cli.click.echo", lambda message, err=False: echoed.append((message, err)))

    cli_module.collaborators_delete_command.callback()

    assert echoed == [
        ("Enter the employee number of the collaborator to delete:", False),
        ("Collaborators delete failed: Faillure Test", True),
    ]