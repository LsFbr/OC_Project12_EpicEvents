import pytest 

from epicevents.services.contracts import get_all_contracts
from epicevents.models.contract import Contract

@pytest.fixture
def seeded_contracts(session):
    session.add_all([
        Contract(total_amount=1000, rest_amount=1000, is_signed=True, client_id=1),
        Contract(total_amount=2000, rest_amount=2000, is_signed=True, client_id=1),
        Contract(total_amount=3000, rest_amount=3000, is_signed=True, client_id=1),
    ])
    session.commit()

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_permission(role, action):
    raise Exception("No permission")

def test_get_all_contracts_ok(session, seeded_contracts, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    

    contracts = get_all_contracts(session)
    assert len(contracts) == 3
    assert contracts[0].total_amount == 1000
    assert contracts[1].total_amount == 2000
    assert contracts[2].total_amount == 3000


def test_get_all_contracts_authentication_failed(session, seeded_contracts, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_contracts(session)


def test_get_all_contracts_no_user(session, seeded_contracts, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_contracts(session)


def test_get_all_contracts_no_permission(session, seeded_contracts, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", raise_no_permission)
    with pytest.raises(Exception):
        get_all_contracts(session)
        

def test_get_all_contracts_no_contracts(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    contracts = get_all_contracts(session)
    assert len(contracts) == 0