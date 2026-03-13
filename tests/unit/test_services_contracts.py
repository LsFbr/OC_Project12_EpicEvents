import pytest 

from decimal import Decimal
from conftest import FakeUser
from epicevents.services.contracts import get_all_contracts, create_contract, update_contract
from epicevents.models.contract import Contract
from epicevents.models.client import Client

@pytest.fixture
def seeded_clients(session):
    session.add_all([
        Client(name="Client 1", email="client1@example.com", phone_number="1234567890", company_name="Company 1", sales_contact_id=1),
        Client(name="Client 2", email="client2@example.com", phone_number="1234567890", company_name="Company 2", sales_contact_id=1),
        Client(name="Client 3", email="client3@example.com", phone_number="1234567890", company_name="Company 3", sales_contact_id=3),
    ])
    session.commit()

@pytest.fixture
def seeded_contracts(session, seeded_clients):
    session.add_all([
        Contract(total_amount=1000, rest_amount=1000, is_signed=True, client_id=1),
        Contract(total_amount=2000, rest_amount=2000, is_signed=True, client_id=2),
        Contract(total_amount=3000, rest_amount=3000, is_signed=True, client_id=3),
    ])
    session.commit()

management_user = FakeUser(user_id=99, role="MANAGEMENT")
sales_user = FakeUser(user_id=1, role="SALES")
support_user = FakeUser(user_id=10, role="SUPPORT")

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_user():
    raise Exception("User no longer exists")

def raise_no_permission(role, action):
    raise Exception("No permission")


# get_all_contracts tests
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
    with pytest.raises(Exception, match="Authentication failed"):
        get_all_contracts(session)


def test_get_all_contracts_no_user(session, seeded_contracts, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    with pytest.raises(Exception, match="User no longer exists"):
        get_all_contracts(session)


def test_get_all_contracts_no_permission(session, seeded_contracts, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", raise_no_permission)
    with pytest.raises(Exception, match="No permission"):
        get_all_contracts(session)
        

def test_get_all_contracts_no_contracts(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)
    contracts = get_all_contracts(session)
    assert len(contracts) == 0


# create_contract tests
def test_create_contract_ok(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    contract = create_contract(
        session=session,
        client_id=1,
        total_amount="1200.50",
        rest_amount="500.25",
        is_signed=True,
    )

    assert contract.id is not None
    assert contract.client_id == 1
    assert contract.total_amount == Decimal("1200.50")
    assert contract.rest_amount == Decimal("500.25")
    assert contract.is_signed is True


def test_create_contract_authentication_failed(session, monkeypatch,fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="1200.50",
            rest_amount="500.25",
        )


def test_create_contract_no_user(session, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="1200.50",
            rest_amount="500.25",
        )


def test_create_contract_no_permission(session, monkeypatch,fake_user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="1200.50",
            rest_amount="500.25",
        )


def test_create_contract_rejects_missing_client_id(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="client_id is required"):
        create_contract(
            session=session,
            client_id=0,
            total_amount="1200.50",
            rest_amount="500.25",
        )


def test_create_contract_rejects_client_not_found(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="client not found"):
        create_contract(
            session=session,
            client_id=999,
            total_amount="1200.50",
            rest_amount="500.25",
        )


def test_create_contract_rejects_missing_total_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="total_amount is required"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="",
            rest_amount="500.25",
        )


def test_create_contract_rejects_missing_rest_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="rest_amount is required"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="1200.50",
            rest_amount="",
        )


def test_create_contract_rejects_invalid_total_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="total_amount must be a valid decimal amount"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="abc",
            rest_amount="500.25",
        )


def test_create_contract_rejects_invalid_rest_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="rest_amount must be a valid decimal amount"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="1200.50",
            rest_amount="abc",
        )


def test_create_contract_rejects_negative_total_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="total_amount must be greater than or equal to 0"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="-1",
            rest_amount="0",
        )


def test_create_contract_rejects_negative_rest_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="rest_amount must be greater than or equal to 0"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="100",
            rest_amount="-1",
        )


def test_create_contract_rejects_rest_amount_exceeds_total_amount(session, seeded_clients, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="rest_amount cannot exceed total_amount"):
        create_contract(
            session=session,
            client_id=1,
            total_amount="100",
            rest_amount="101",
        )


# update_contract tests
def test_update_contract_ok_as_management(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    contract_updated = update_contract(
        session=session,
        contract_id=1,
        total_amount="1500.00",
        rest_amount="750.00",
        is_signed=False,
    )

    assert contract_updated.id == 1
    assert contract_updated.total_amount == Decimal("1500.00")
    assert contract_updated.rest_amount == Decimal("750.00")
    assert contract_updated.is_signed is False


def test_update_contract_ok_as_sales_owned(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)

    contract_updated = update_contract(
        session=session,
        contract_id=1,
        total_amount="1400.00",
        rest_amount="400.00",
        is_signed=True,
    )

    assert contract_updated.id == 1
    assert contract_updated.total_amount == Decimal("1400.00")
    assert contract_updated.rest_amount == Decimal("400.00")
    assert contract_updated.is_signed is True


def test_update_contract_authentication_failed(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(Exception, match="Authentication failed"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="1500.00",
        )


def test_update_contract_no_user(session, seeded_clients, seeded_contracts, monkeypatch):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)

    with pytest.raises(Exception, match="User no longer exists"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="1500.00",
        )


def test_update_contract_no_permission_as_support(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: support_user)

    with pytest.raises(PermissionError, match="No permission"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="1500.00",
        )


def test_update_contract_rejects_missing_contract_id(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="contract_id is required"):
        update_contract(
            session=session,
            contract_id=0,
            total_amount="1500.00",
        )


def test_update_contract_rejects_no_fields(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="no fields to update"):
        update_contract(
            session=session,
            contract_id=1,
        )


def test_update_contract_rejects_contract_not_found(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="contract not found"):
        update_contract(
            session=session,
            contract_id=999,
            total_amount="1500.00",
        )


def test_update_contract_rejects_not_owned_contract(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)

    with pytest.raises(PermissionError, match="you are not the sales contact of this contract"):
        update_contract(
            session=session,
            contract_id=3,
            total_amount="1500.00",
        )


def test_update_contract_rejects_missing_client_id(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="client_id is required"):
        update_contract(
            session=session,
            contract_id=1,
            client_id=0,
        )


def test_update_contract_rejects_client_not_found(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="client not found"):
        update_contract(
            session=session,
            contract_id=1,
            client_id=999,
        )


def test_update_contract_rejects_sales_changing_to_unowned_client(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)

    with pytest.raises(PermissionError, match="you are not the sales contact of this client"):
        update_contract(
            session=session,
            contract_id=1,
            client_id=3,
        )


def test_update_contract_allows_sales_changing_to_owned_client(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)

    contract_updated = update_contract(
        session=session,
        contract_id=1,
        client_id=2,
    )

    assert contract_updated.client_id == 2


def test_update_contract_rejects_missing_total_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="total_amount is required"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="",
        )


def test_update_contract_rejects_invalid_total_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="total_amount must be a valid decimal amount"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="abc",
        )


def test_update_contract_rejects_negative_total_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="total_amount must be greater than or equal to 0"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="-1",
        )


def test_update_contract_rejects_missing_rest_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="rest_amount is required"):
        update_contract(
            session=session,
            contract_id=1,
            rest_amount="",
        )


def test_update_contract_rejects_invalid_rest_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="rest_amount must be a valid decimal amount"):
        update_contract(
            session=session,
            contract_id=1,
            rest_amount="abc",
        )


def test_update_contract_rejects_negative_rest_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="rest_amount must be greater than or equal to 0"):
        update_contract(
            session=session,
            contract_id=1,
            rest_amount="-1",
        )


def test_update_contract_rejects_rest_amount_exceeds_total_amount_when_only_rest_changes(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="rest_amount cannot exceed total_amount"):
        update_contract(
            session=session,
            contract_id=1,
            rest_amount="2000.00",
        )


def test_update_contract_rejects_total_amount_below_existing_rest_amount(session, seeded_clients, seeded_contracts, monkeypatch):

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)

    with pytest.raises(ValueError, match="rest_amount cannot exceed total_amount"):
        update_contract(
            session=session,
            contract_id=1,
            total_amount="500.00",
        )