import pytest

from tests.conftest import FakeClient, FakeSession
from epicevents.exceptions import NotLoggedInError, UserNotFoundError, BusinessAuthorizationError, BusinessValidationError
from epicevents.models.client import Client
from epicevents.services.clients import (
    get_all_clients,
    create_client,
    update_client,
)


def raise_authentication_failed():
    raise NotLoggedInError("Authentication failed")


def raise_no_user():
    raise UserNotFoundError("User no longer exists")


def raise_no_permission(role, action):
    raise BusinessAuthorizationError("No permission")


def allow_authenticated_user(monkeypatch, user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)


@pytest.fixture
def owned_client(sales_user):
    return FakeClient(
        client_id=1,
        name="Client One",
        email="client1@example.com",
        phone_number="+33611111111",
        company_name="Company One",
        informations="Info One",
        sales_contact_id=sales_user.id,
    )


@pytest.fixture
def second_owned_client(sales_user):
    return FakeClient(
        client_id=2,
        name="Client Two",
        email="client2@example.com",
        phone_number="+33622222222",
        company_name="Company Two",
        informations="Info Two",
        sales_contact_id=sales_user.id,
    )


@pytest.fixture
def unowned_client():
    return FakeClient(
        client_id=3,
        name="Client Three",
        email="client3@example.com",
        phone_number="+33633333333",
        company_name="Company Three",
        informations="Info Three",
        sales_contact_id=999,
    )


# -------------------------
# get_all_clients
# -------------------------

def test_get_all_clients_ok(monkeypatch, fake_user, owned_client, second_owned_client, unowned_client):
    session = FakeSession(execute_items=[owned_client, second_owned_client, unowned_client])

    allow_authenticated_user(monkeypatch, fake_user)

    clients = get_all_clients(session)

    assert len(clients) == 3
    assert clients[0] == owned_client
    assert clients[1] == second_owned_client
    assert clients[2] == unowned_client


def test_get_all_clients_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(NotLoggedInError, match="Authentication failed"):
        get_all_clients(session)


def test_get_all_clients_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(UserNotFoundError, match="User no longer exists"):
        get_all_clients(session)


def test_get_all_clients_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        get_all_clients(session)


def test_get_all_clients_no_clients(monkeypatch, fake_user):
    session = FakeSession(execute_items=[])

    allow_authenticated_user(monkeypatch, fake_user)

    clients = get_all_clients(session)

    assert clients == []


# -------------------------
# create_client
# -------------------------

def test_create_client_ok(monkeypatch, fake_user):
    session = FakeSession(query_map={Client: []})

    allow_authenticated_user(monkeypatch, fake_user)

    client = create_client(
        session=session,
        informations=" New client infos ",
        name=" New Client ",
        email="NewClient@example.com",
        phone_number="+33612345678",
        company_name=" New Company ",
    )

    assert client.id == 999
    assert client.informations == "New client infos"
    assert client.name == "New Client"
    assert client.email == "newclient@example.com"
    assert client.phone_number == "+33612345678"
    assert client.company_name == "New Company"
    assert client.sales_contact_id == fake_user.id
    assert session.committed is True


def test_create_client_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(NotLoggedInError, match="Authentication failed"):
        create_client(session, "infos", "Client", "client@example.com", "+33612345678", "Company")


def test_create_client_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(UserNotFoundError, match="User no longer exists"):
        create_client(session, "infos", "Client", "client@example.com", "+33612345678", "Company")


def test_create_client_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        create_client(session, "infos", "Client", "client@example.com", "+33612345678", "Company")


def test_create_client_rejects_missing_name(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="name is required"):
        create_client(session, "infos", "", "client@example.com", "+33612345678", "Company")


def test_create_client_rejects_missing_email(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="email is required"):
        create_client(session, "infos", "Client", "", "+33612345678", "Company")


def test_create_client_rejects_invalid_email(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="email is invalid"):
        create_client(session, "infos", "Client", "not-an-email", "+33612345678", "Company")


def test_create_client_rejects_duplicate_email(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="email already exists"):
        create_client(session, "infos", "Client", "CLIENT1@example.com", "+33612345678", "Company")


def test_create_client_rejects_missing_phone_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="phone_number is required"):
        create_client(session, "infos", "Client", "client@example.com", "", "Company")


def test_create_client_rejects_invalid_phone_number(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="phone_number is invalid"):
        create_client(session, "infos", "Client", "client@example.com", "abc", "Company")


def test_create_client_rejects_missing_company_name(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="company_name is required"):
        create_client(session, "infos", "Client", "client@example.com", "+33612345678", "")


# -------------------------
# update_client
# -------------------------

def test_update_client_ok(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    client_updated = update_client(
        session=session,
        client_id=owned_client.id,
        informations=" updated infos ",
        name=" Updated Client 1 ",
        email="UpdatedClient1@example.com",
        phone_number="+33987654321",
        company_name=" Updated Company 1 ",
    )

    assert client_updated.id == owned_client.id
    assert client_updated.informations == "updated infos"
    assert client_updated.name == "Updated Client 1"
    assert client_updated.email == "updatedclient1@example.com"
    assert client_updated.phone_number == "+33987654321"
    assert client_updated.company_name == "Updated Company 1"
    assert client_updated.sales_contact_id == sales_user.id
    assert session.committed is True


def test_update_client_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(NotLoggedInError, match="Authentication failed"):
        update_client(session, 1, name="Updated Client")


def test_update_client_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(UserNotFoundError, match="User no longer exists"):
        update_client(session, 1, name="Updated Client")


def test_update_client_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        update_client(session, 1, name="Updated Client")


def test_update_client_rejects_missing_client_id(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="client_id is required"):
        update_client(session, 0, name="Updated Client")


def test_update_client_rejects_no_fields(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="no fields to update"):
        update_client(session, 1)


def test_update_client_rejects_client_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Client: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="client not found"):
        update_client(session, 999, name="Updated Client")


def test_update_client_rejects_not_owned_client(monkeypatch, sales_user, unowned_client):
    session = FakeSession(query_map={Client: [unowned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessAuthorizationError, match="You are not the sales contact of this client"):
        update_client(session, unowned_client.id, name="Updated Client")


def test_update_client_rejects_missing_name(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="name is required"):
        update_client(session, owned_client.id, name="")


def test_update_client_rejects_missing_email(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="email is required"):
        update_client(session, owned_client.id, email="")


def test_update_client_rejects_invalid_email(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="email is invalid"):
        update_client(session, owned_client.id, email="not-an-email")


def test_update_client_rejects_existing_email(monkeypatch, sales_user, owned_client, second_owned_client):
    session = FakeSession(query_map={Client: [owned_client, second_owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="email already exists"):
        update_client(session, owned_client.id, email=second_owned_client.email)


def test_update_client_rejects_missing_phone_number(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="phone_number is required"):
        update_client(session, owned_client.id, phone_number="")


def test_update_client_rejects_invalid_phone_number(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="phone_number is invalid"):
        update_client(session, owned_client.id, phone_number="abc")


def test_update_client_rejects_missing_company_name(monkeypatch, sales_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, sales_user)

    with pytest.raises(BusinessValidationError, match="company_name is required"):
        update_client(session, owned_client.id, company_name="")
