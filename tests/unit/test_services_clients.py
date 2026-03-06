import pytest 

from epicevents.services.clients import get_all_clients
from epicevents.models.client import Client


@pytest.fixture
def seeded_clients(session):
    session.add_all([
        Client(name="Client 1", email="client1@example.com", phone_number="1234567890", company_name="Company 1", sales_contact_id=1),
        Client(name="Client 2", email="client2@example.com", phone_number="1234567890", company_name="Company 2", sales_contact_id=1),
        Client(name="Client 3", email="client3@example.com", phone_number="1234567890", company_name="Company 3", sales_contact_id=1),
    ])
    session.commit()

class FakeRole:
    def __init__(self):
        self.name = "fake_role"

class FakeUser:
    def __init__(self):
        self.role = FakeRole()

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_permission(role, action):
    raise Exception("No permission")

def test_get_all_clients_ok(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    

    clients = get_all_clients(session)
    assert len(clients) == 3
    assert clients[0].name == "Client 1"
    assert clients[1].name == "Client 2"
    assert clients[2].name == "Client 3"


def test_get_all_clients_authentication_failed(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_clients(session)


def test_get_all_clients_no_user(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_clients(session)


def test_get_all_clients_no_permission(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.clients.require_permission", raise_no_permission)
    with pytest.raises(Exception):
        get_all_clients(session)
        

def test_get_all_clients_no_clients(session, monkeypatch):
    monkeypatch.setattr("epicevents.services.clients.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.clients.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.clients.require_permission", lambda role, action: None)
    clients = get_all_clients(session)
    assert len(clients) == 0