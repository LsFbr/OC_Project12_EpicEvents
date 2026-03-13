import pytest 

from epicevents.services.clients import get_all_clients, create_client, update_client
from epicevents.models.client import Client


@pytest.fixture
def seeded_clients(session):
    session.add_all([
        Client(name="Client 1", email="client1@example.com", phone_number="1234567890", company_name="Company 1", sales_contact_id=1),
        Client(name="Client 2", email="client2@example.com", phone_number="1234567890", company_name="Company 2", sales_contact_id=2),
        Client(name="Client 3", email="client3@example.com", phone_number="1234567890", company_name="Company 3", sales_contact_id=3),
    ])
    session.commit()

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_user():
    raise Exception("User no longer exists")

def raise_no_permission(role, action):
    raise Exception("No permission")

# get_all_clients tests
def test_get_all_clients_ok(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    

    clients = get_all_clients(session)
    assert len(clients) == 3
    assert clients[0].name == "Client 1"
    assert clients[1].name == "Client 2"
    assert clients[2].name == "Client 3"


def test_get_all_clients_authentication_failed(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    with pytest.raises(Exception, match="Authentication failed"):
        get_all_clients(session)


def test_get_all_clients_no_user(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    with pytest.raises(Exception, match="User no longer exists"):
        get_all_clients(session)


def test_get_all_clients_no_permission(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)
    with pytest.raises(Exception, match="No permission"):
        get_all_clients(session)
        

def test_get_all_clients_no_clients(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    clients = get_all_clients(session)
    assert len(clients) == 0


# create_client tests
def test_create_client_ok(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    client = create_client(
        session=session,
        informations="New client infos",
        name="New Client",
        email="NewClient@example.com",
        phone_number="+33612345678",
        company_name="New Company",
    )

    assert client.id is not None
    assert client.informations == "New client infos"
    assert client.name == "New Client"
    assert client.email == "newclient@example.com"
    assert client.phone_number == "+33612345678"
    assert client.company_name == "New Company"
    assert client.sales_contact_id == fake_user.id


def test_create_client_authentication_failed(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_no_user(session, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_no_permission(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_rejects_missing_name(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="name is required"):
        create_client(
            session=session,
            informations="infos",
            name="",
            email="client@example.com",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_rejects_missing_email(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is required"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_rejects_invalid_email(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is invalid"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="not-an-email",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_rejects_duplicate_email(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email already exists"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="CLIENT1@example.com",
            phone_number="+33612345678",
            company_name="Company",
        )


def test_create_client_rejects_missing_phone_number(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="phone_number is required"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="",
            company_name="Company",
        )


def test_create_client_rejects_invalid_phone_number(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="phone_number is invalid"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="abc",
            company_name="Company",
        )


def test_create_client_rejects_missing_company_name(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="company_name is required"):
        create_client(
            session=session,
            informations="infos",
            name="Client",
            email="client@example.com",
            phone_number="+33612345678",
            company_name="",
        )


# update_client tests
def test_update_client_ok(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    client_to_update = session.query(Client).filter(Client.id == 1).one()

    client_updated = update_client(
        session=session,
        client_id=client_to_update.id,
        informations="updated infos",
        name="Updated Client 1",
        email="updatedclient1@example.com",
        phone_number="+33987654321",
        company_name="Updated Company 1",
    )

    assert client_updated.id == client_to_update.id
    assert client_updated.informations == "updated infos"
    assert client_updated.name == "Updated Client 1"
    assert client_updated.email == "updatedclient1@example.com"
    assert client_updated.phone_number == "+33987654321"
    assert client_updated.company_name == "Updated Company 1"
    assert client_updated.sales_contact_id == 1


def test_update_client_authentication_failed(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        update_client(
            session=session,
            client_id=1,
            name="Updated Client",
        )


def test_update_client_no_user(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        update_client(
            session=session,
            client_id=1,
            name="Updated Client",
        )


def test_update_client_no_permission(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        update_client(
            session=session,
            client_id=1,
            name="Updated Client",
        )


def test_update_client_rejects_missing_client_id(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="client_id is required"):
        update_client(
            session=session,
            client_id=0,
            name="Updated Client",
        )


def test_update_client_rejects_no_fields(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="no fields to update"):
        update_client(
            session=session,
            client_id=1,
        )


def test_update_client_rejects_client_not_found(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="client not found"):
        update_client(
            session=session,
            client_id=999,
            name="Updated Client",
        )


def test_update_client_rejects_not_owned_client(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(PermissionError, match="You are not the sales contact of this client"):
        update_client(
            session=session,
            client_id=3,
            name="Updated Client",
        )


def test_update_client_rejects_missing_name(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="name is required"):
        update_client(
            session=session,
            client_id=1,
            name="",
        )


def test_update_client_rejects_missing_email(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is required"):
        update_client(
            session=session,
            client_id=1,
            email="",
        )


def test_update_client_rejects_invalid_email(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email is invalid"):
        update_client(
            session=session,
            client_id=1,
            email="not-an-email",
        )


def test_update_client_rejects_existing_email(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="email already exists"):
        update_client(
            session=session,
            client_id=1,
            email="client2@example.com",
        )


def test_update_client_rejects_missing_phone_number(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="phone_number is required"):
        update_client(
            session=session,
            client_id=1,
            phone_number="",
        )


def test_update_client_rejects_invalid_phone_number(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="phone_number is invalid"):
        update_client(
            session=session,
            client_id=1,
            phone_number="abc",
        )


def test_update_client_rejects_missing_company_name(session, seeded_clients, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="company_name is required"):
        update_client(
            session=session,
            client_id=1,
            company_name="",
        )