import pytest

from epicevents.cli import cli as cli_module
from tests.conftest import FakeUser, FakeClient, FakeContract, FakeEvent
from epicevents.exceptions import InvalidCredentialsError, NotLoggedInError

def capture_echo(monkeypatch):
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.cli.click.echo",
        lambda message, err=False: echoed.append((message, err)),
    )

    return echoed


def allow_cli_auth(monkeypatch, user):
    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: user)
    monkeypatch.setattr("epicevents.cli.cli.require_permission", lambda role_name, action: None)


# -------------------------
# login_command / logout_command
# -------------------------

def test_login_command_success(monkeypatch):
    echoed = capture_echo(monkeypatch)
    called = {}

    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "user@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")

    def fake_login(email, password):
        called["email"] = email
        called["password"] = password

    monkeypatch.setattr("epicevents.cli.cli.login", fake_login)

    cli_module.login_command.callback()

    assert called == {"email": "user@example.com", "password": "Password123"}
    assert echoed == [("Login successful", False)]


def test_login_command_failure(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "user@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")

    def login_failure(*args, **kwargs):
        raise InvalidCredentialsError("Invalid email or password")

    monkeypatch.setattr("epicevents.cli.cli.login", login_failure)

    cli_module.login_command.callback()

    assert echoed == [("Login failed: Invalid email or password", True)]


def test_login_command_unexpected_error(monkeypatch):
    echoed = capture_echo(monkeypatch)
    captured = {}

    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "user@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")

    def login_unexpected_error(*args, **kwargs):
        raise RuntimeError("unexpected error test")

    def fake_capture(exc, **context):
        captured["exc"] = exc
        captured["context"] = context

    monkeypatch.setattr("epicevents.cli.cli.capture_unexpected_exception", fake_capture)
    monkeypatch.setattr("epicevents.cli.cli.login", login_unexpected_error)

    cli_module.login_command.callback()

    assert isinstance(captured["exc"], RuntimeError)
    assert str(captured["exc"]) == "unexpected error test"
    assert captured["context"] == {"action": "Login"}
    assert echoed == [("Login failed: unexpected error", True)]


def test_logout_command_success(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr("epicevents.cli.cli.logout", lambda: None)

    cli_module.logout_command.callback()

    assert echoed == [("Logout successful", False)]


def test_logout_command_failure(monkeypatch):
    echoed = capture_echo(monkeypatch)

    def logout_failure(*args, **kwargs):
        raise NotLoggedInError("You were not logged in")

    monkeypatch.setattr("epicevents.cli.cli.logout", logout_failure)


    cli_module.logout_command.callback()

    assert echoed == [("Logout failed: You were not logged in", True)]


def test_logout_command_unexpected_error(monkeypatch):
    echoed = capture_echo(monkeypatch)
    captured = {}

    def logout_unexpected_error(*args, **kwargs):
        raise RuntimeError("unexpected error test")

    def fake_capture(exc, **context):
        captured["exc"] = exc
        captured["context"] = context

    monkeypatch.setattr("epicevents.cli.cli.capture_unexpected_exception", fake_capture)
    monkeypatch.setattr("epicevents.cli.cli.logout", logout_unexpected_error)

    cli_module.logout_command.callback()

    assert isinstance(captured["exc"], RuntimeError)
    assert str(captured["exc"]) == "unexpected error test"
    assert captured["context"] == {"action": "Logout"}
    assert echoed == [("Logout failed: unexpected error", True)]
# -------------------------
# collaborators
# -------------------------

def test_collaborators_list_command_success(monkeypatch, fake_session, management_user):
    echoed = capture_echo(monkeypatch)

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

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_collaborators", lambda session: [collaborator_1, collaborator_2])

    cli_module.collaborators_list_command.callback()

    assert echoed == [
        ("ID | Employee Number | Full Name | Email | Role", False),
        ("--------------------------------------------------", False),
        ("2 | 1 | User One | userone@example.com | MANAGEMENT", False),
        ("3 | 2 | User Two | usertwo@example.com | SALES", False),
    ]


def test_collaborators_create_command_success(monkeypatch, fake_session, management_user):
    echoed = capture_echo(monkeypatch)

    collaborator = FakeUser(
        user_id=4,
        employee_number=4,
        full_name="Collab Four",
        email="collabfour@example.com",
        role_name="SALES",
    )

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 4)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: "Collab Four")
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "collabfour@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda *args, **kwargs: "SALES")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")
    monkeypatch.setattr(
        "epicevents.cli.cli.create_collaborator",
        lambda *args, **kwargs: collaborator,
    )

    cli_module.collaborators_create_command.callback()

    assert echoed == [
        ("Enter the details for the new collaborator (marked with * are required):", False),
        ("Collaborator Collab Four created successfully.", False),
        ("ID | Employee Number | Full Name | Email | Role", False),
        ("--------------------------------------------------", False),
        ("4 | 4 | Collab Four | collabfour@example.com | SALES", False),
    ]


def test_collaborators_update_command_failure(monkeypatch, fake_session, management_user):
    echoed = capture_echo(monkeypatch)

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: "Updated User")
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "updated@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda *args, **kwargs: "SUPPORT")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")

    def update_collaborator_failure(*args, **kwargs):
        raise ValueError("Failure test")

    monkeypatch.setattr("epicevents.cli.cli.update_collaborator", update_collaborator_failure)

    cli_module.collaborators_update_command.callback()

    assert echoed == [
        ("Enter the details for the collaborator to update (marked with * are required):", False),
        ("Collaborators update failed: Failure test", True),
    ]


def test_collaborators_update_command_unexpected_error(monkeypatch, fake_session, management_user):
    echoed = capture_echo(monkeypatch)
    captured = {}

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: "Updated User")
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "updated@example.com")
    monkeypatch.setattr("epicevents.cli.cli.prompt_role", lambda *args, **kwargs: "SUPPORT")
    monkeypatch.setattr("epicevents.cli.cli.prompt_password", lambda *args, **kwargs: "Password123")

    def update_collaborator_unexpected_error(*args, **kwargs):
        raise RuntimeError("unexpected error test")

    def fake_capture(exc, **context):
        captured["exc"] = exc
        captured["context"] = context

    monkeypatch.setattr("epicevents.cli.cli.update_collaborator", update_collaborator_unexpected_error)
    monkeypatch.setattr("epicevents.cli.cli.capture_unexpected_exception", fake_capture)

    cli_module.collaborators_update_command.callback()

    assert isinstance(captured["exc"], RuntimeError)
    assert str(captured["exc"]) == "unexpected error test"
    assert captured["context"] == {"action": "Collaborators update"}
    assert echoed == [
        ("Enter the details for the collaborator to update (marked with * are required):", False),
        ("Collaborators update failed: unexpected error", True),
    ]


def test_collaborators_delete_command_success(monkeypatch, fake_session, management_user):
    echoed = capture_echo(monkeypatch)

    collaborator = FakeUser(
        user_id=1,
        employee_number=1,
        full_name="User One",
        email="userone@example.com",
        role_name="MANAGEMENT",
    )

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.delete_collaborator", lambda *args, **kwargs: collaborator)

    cli_module.collaborators_delete_command.callback()

    assert echoed == [
        ("Enter the employee number of the collaborator to delete:", False),
        ("Collaborator User One deleted successfully.", False),
    ]


# -------------------------
# clients
# -------------------------

def test_clients_list_command_success(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    client = FakeClient(
        client_id=1,
        name="Client One",
        email="client1@example.com",
        phone_number="+33611111111",
        company_name="Company One",
        informations="Info One",
        sales_contact_id=sales_user.id,
    )
    client.sales_contact = sales_user

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_clients", lambda session: [client])

    cli_module.clients_list_command.callback()

    assert echoed == [
        ("ID | Name | Email | Phone | Company | Informations | Sales Contact ID | Sales Contact Name", False),
        ("--------------------------------------------------------", False),
        (f"1 | Client One | client1@example.com | +33611111111 | Company One | Info One | {sales_user.id} | {sales_user.full_name}", False),
    ]


def test_clients_create_command_success(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    client = FakeClient(
        client_id=1,
        name="Client One",
        email="client1@example.com",
        phone_number="+33611111111",
        company_name="Company One",
        informations="Info One",
        sales_contact_id=sales_user.id,
    )
    client.sales_contact = sales_user

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)

    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_text",
        lambda *args, **kwargs: {
            "Name": "Client One",
            "Phone Number": "+33611111111",
            "Company Name": "Company One",
            "Informations": "Info One",
        }[args[0]],
    )
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: "client1@example.com")
    monkeypatch.setattr("epicevents.cli.cli.create_client", lambda *args, **kwargs: client)

    cli_module.clients_create_command.callback()

    assert echoed[0] == ("Enter the details for the new client (marked with * are required):", False)
    assert echoed[1] == ("Client Client One created successfully.", False)


def test_clients_update_command_failure(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_email", lambda *args, **kwargs: None)

    def update_client_failure(*args, **kwargs):
        raise ValueError("Failure test")

    monkeypatch.setattr("epicevents.cli.cli.update_client", update_client_failure)

    cli_module.clients_update_command.callback()

    assert echoed == [
        ("Enter the details for the client to update (marked with * are required):", False),
        ("Clients update failed: Failure test", True),
    ]


# -------------------------
# contracts
# -------------------------

def test_contracts_list_command_success(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    client = FakeClient(
        client_id=1,
        name="Client One",
        email="client1@example.com",
        phone_number="+33611111111",
        company_name="Company One",
        informations="Info One",
        sales_contact_id=sales_user.id,
    )
    client.sales_contact = sales_user

    contract = FakeContract(
        contract_id=1,
        total_amount="1000.00",
        rest_amount="500.00",
        is_signed=True,
        client=client,
    )

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.has_permission", lambda *args, **kwargs: True)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_contracts", lambda *args, **kwargs: [contract])

    cli_module.contracts_list_command.callback(False, False, False, False)

    assert echoed[0] == ("ID | Total Amount | Rest Amount | Signed | Client ID | Client Name | Support Contact ID | Support Contact Name", False)
    assert echoed[2] == (f"1 | 1000.00 | 500.00 | Yes | 1 | Client One | {sales_user.id} | {sales_user.full_name}", False)


def test_contracts_create_command_success(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    client = FakeClient(client_id=1, name="Client One", sales_contact_id=sales_user.id)
    client.sales_contact = sales_user
    contract = FakeContract(contract_id=1, total_amount="1000.00", rest_amount="500.00", is_signed=True, client=client)

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: "1000.00" if args[0] == "Total Amount" else "500.00")
    monkeypatch.setattr("epicevents.cli.cli.prompt_bool", lambda *args, **kwargs: True)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.create_contract", lambda *args, **kwargs: contract)

    cli_module.contracts_create_command.callback()

    assert echoed[0] == ("Enter the details for the new contract (marked with * are required):", False)
    assert echoed[1] == ("Contract 1 created successfully.", False)


def test_contracts_update_command_failure(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr("epicevents.cli.cli.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.cli.cli.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.cli.cli.has_permission", lambda role, action: True)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_bool", lambda *args, **kwargs: None)

    def update_contract_failure(*args, **kwargs):
        raise ValueError("Failure test")

    monkeypatch.setattr("epicevents.cli.cli.update_contract", update_contract_failure)

    cli_module.contracts_update_command.callback()

    assert echoed == [
        ("Enter the details for the contract to update (marked with * are required):", False),
        ("Contracts update failed: Failure test", True),
    ]


# -------------------------
# events
# -------------------------

def test_events_list_command_success(monkeypatch, fake_session, support_user):
    echoed = capture_echo(monkeypatch)

    event = FakeEvent(
        event_id=1,
        title="Event One",
        notes="Notes",
        location="Paris",
        attendees=50,
        contract_id=1,
        support_contact_id=support_user.id,
    )
    event.support_contact = support_user

    allow_cli_auth(monkeypatch, support_user)
    monkeypatch.setattr("epicevents.cli.cli.has_permission", lambda *args, **kwargs: True)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.get_all_events", lambda *args, **kwargs: [event])

    cli_module.events_list_command.callback(None, False)

    assert echoed[0] == ("ID | Title | Location | Attendees | Start | End | Contract ID | Support Contact ID | Support Contact Name", False)
    assert echoed[2] == (f"1 | Event One | Paris | 50 | 2026-01-01 09:00:00 | 2026-01-01 17:00:00 | 1 | {support_user.id} | {support_user.full_name}", False)


def test_events_create_command_success(monkeypatch, fake_session, sales_user):
    echoed = capture_echo(monkeypatch)

    event = FakeEvent(
        event_id=1,
        title="Event One",
        notes="Notes",
        location="Paris",
        attendees=50,
        contract_id=1,
        support_contact_id=None,
    )
    event.support_contact = None

    allow_cli_auth(monkeypatch, sales_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_text",
        lambda *args, **kwargs: {
            "Title": "Event One",
            "Notes": "Notes",
            "Location": "Paris",
        }.get(args[0], None),
    )
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 50 if args[0] == "Attendees" else 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_datetime", lambda *args, **kwargs: "2026-01-01 10:00:00")
    monkeypatch.setattr("epicevents.cli.cli.create_event", lambda *args, **kwargs: event)

    cli_module.events_create_command.callback()

    assert echoed[0] == ("Enter the details for the new event (marked with * are required):", False)
    assert echoed[1] == ("Event Event One created successfully.", False)


def test_events_update_command_failure(monkeypatch, fake_session, support_user):
    echoed = capture_echo(monkeypatch)

    allow_cli_auth(monkeypatch, support_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.cli.cli.prompt_int", lambda *args, **kwargs: 1)
    monkeypatch.setattr("epicevents.cli.cli.prompt_text", lambda *args, **kwargs: None)
    monkeypatch.setattr("epicevents.cli.cli.prompt_datetime", lambda *args, **kwargs: None)

    def update_event_failure(*args, **kwargs):
        raise ValueError("Failure test")

    monkeypatch.setattr("epicevents.cli.cli.update_event", update_event_failure)

    cli_module.events_update_command.callback()

    assert echoed == [
        ("Enter the details for the event to update (marked with * are required):", False),
        ("Events update failed: Failure test", True),
    ]


def test_events_assign_support_command_success(monkeypatch, fake_session, management_user, support_user):
    echoed = capture_echo(monkeypatch)

    event = FakeEvent(
        event_id=1,
        title="Event One",
        notes="Notes",
        location="Paris",
        attendees=50,
        contract_id=1,
        support_contact_id=support_user.id,
    )
    event.support_contact = support_user

    allow_cli_auth(monkeypatch, management_user)
    monkeypatch.setattr("epicevents.cli.cli.SessionLocal", lambda: fake_session)
    monkeypatch.setattr(
        "epicevents.cli.cli.prompt_int",
        lambda *args, **kwargs: 1 if args[0] == "Event ID" else support_user.id,
    )
    monkeypatch.setattr("epicevents.cli.cli.assign_support", lambda *args, **kwargs: event)

    cli_module.events_assign_support_command.callback()

    assert echoed[0] == ("Enter the details to assign support to an event (marked with * are required):", False)
    assert echoed[1] == ("Support assignment updated for event Event One.", False)