import pytest
from decimal import Decimal

from conftest import FakeClient, FakeContract, FakeSession

from epicevents.models.client import Client
from epicevents.models.contract import Contract
from epicevents.services.contracts import (
    _to_decimal,
    get_all_contracts,
    create_contract,
    update_contract,
)
from epicevents.security.permissions import (
    CONTRACT_UPDATE_ANY,
    CONTRACT_UPDATE_OWNED,
)


def raise_authentication_failed():
    raise Exception("Authentication failed")


def raise_no_user():
    raise Exception("User no longer exists")


def raise_no_permission(role_name, action):
    raise PermissionError("No permission")


def allow_authenticated_user(monkeypatch, user):
    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)


@pytest.fixture
def owned_client(sales_user):
    return FakeClient(client_id=1, sales_contact_id=sales_user.id)


@pytest.fixture
def second_owned_client(sales_user):
    return FakeClient(client_id=2, sales_contact_id=sales_user.id)


@pytest.fixture
def unowned_client():
    return FakeClient(client_id=3, sales_contact_id=999)


@pytest.fixture
def owned_contract(owned_client):
    return FakeContract(
        contract_id=1,
        total_amount=Decimal("1000.00"),
        rest_amount=Decimal("500.00"),
        is_signed=True,
        client=owned_client,
    )


@pytest.fixture
def second_owned_contract(second_owned_client):
    return FakeContract(
        contract_id=2,
        total_amount=Decimal("2000.00"),
        rest_amount=Decimal("0.00"),
        is_signed=False,
        client=second_owned_client,
    )


@pytest.fixture
def unowned_contract(unowned_client):
    return FakeContract(
        contract_id=3,
        total_amount=Decimal("3000.00"),
        rest_amount=Decimal("1500.00"),
        is_signed=True,
        client=unowned_client,
    )


# -------------------------
# _to_decimal
# -------------------------

def test_to_decimal_ok():
    assert _to_decimal("1200.50", "total_amount") == Decimal("1200.50")


def test_to_decimal_rejects_missing_value():
    with pytest.raises(ValueError, match="total_amount is required"):
        _to_decimal("", "total_amount")


def test_to_decimal_rejects_invalid_value():
    with pytest.raises(ValueError, match="total_amount must be a valid decimal amount"):
        _to_decimal("abc", "total_amount")


# -------------------------
# get_all_contracts
# -------------------------

def test_get_all_contracts_ok(monkeypatch, fake_user, owned_contract, second_owned_contract):
    session = FakeSession(execute_items=[owned_contract, second_owned_contract])

    allow_authenticated_user(monkeypatch, fake_user)

    contracts = get_all_contracts(session)

    assert len(contracts) == 2
    assert contracts[0] == owned_contract
    assert contracts[1] == second_owned_contract


def test_get_all_contracts_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        get_all_contracts(session)


def test_get_all_contracts_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        get_all_contracts(session)


def test_get_all_contracts_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        get_all_contracts(session)


def test_get_all_contracts_rejects_combined_signed_filters(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="signed and not_signed filters cannot be used together"):
        get_all_contracts(session, signed=True, not_signed=True)


def test_get_all_contracts_rejects_combined_paid_filters(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="paid and unpaid filters cannot be used together"):
        get_all_contracts(session, paid=True, unpaid=True)


def test_get_all_contracts_signed_filter_ok(monkeypatch, fake_user, owned_contract):
    session = FakeSession(execute_items=[owned_contract])

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: True)

    contracts = get_all_contracts(session, signed=True)

    assert len(contracts) == 1
    assert contracts[0] == owned_contract


def test_get_all_contracts_signed_filter_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: False)

    with pytest.raises(PermissionError, match="only sales can filter by signed contracts"):
        get_all_contracts(session, signed=True)


def test_get_all_contracts_paid_filter_ok(monkeypatch, fake_user, second_owned_contract):
    session = FakeSession(execute_items=[second_owned_contract])

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: True)

    contracts = get_all_contracts(session, paid=True)

    assert len(contracts) == 1
    assert contracts[0] == second_owned_contract


def test_get_all_contracts_paid_filter_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: False)

    with pytest.raises(PermissionError, match="only sales can filter by paid contracts"):
        get_all_contracts(session, paid=True)


# -------------------------
# create_contract
# -------------------------

def test_create_contract_ok(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    contract = create_contract(
        session=session,
        client_id=owned_client.id,
        total_amount="1200.50",
        rest_amount="500.25",
        is_signed=True,
    )

    assert contract.client_id == owned_client.id
    assert contract.total_amount == Decimal("1200.50")
    assert contract.rest_amount == Decimal("500.25")
    assert contract.is_signed is True
    assert session.committed is True


def test_create_contract_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        create_contract(session, 1, "1200.50", "500.25")


def test_create_contract_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        create_contract(session, 1, "1200.50", "500.25")


def test_create_contract_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        create_contract(session, 1, "1200.50", "500.25")


def test_create_contract_rejects_missing_client_id(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="client_id is required"):
        create_contract(session, 0, "1200.50", "500.25")


def test_create_contract_rejects_client_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Client: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="client not found"):
        create_contract(session, 999, "1200.50", "500.25")


def test_create_contract_rejects_invalid_total_amount(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="total_amount must be a valid decimal amount"):
        create_contract(session, owned_client.id, "abc", "500.25")


def test_create_contract_rejects_invalid_rest_amount(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(ValueError, match="rest_amount must be a valid decimal amount"):
        create_contract(session, owned_client.id, "1200.50", "abc")


def test_create_contract_rejects_negative_total_amount(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="total_amount must be greater than or equal to 0"):
        create_contract(session, owned_client.id, "-1", "0")


def test_create_contract_rejects_negative_rest_amount(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="rest_amount must be greater than or equal to 0"):
        create_contract(session, owned_client.id, "100", "-1")


def test_create_contract_rejects_rest_amount_exceeds_total_amount(monkeypatch, fake_user, owned_client):
    session = FakeSession(query_map={Client: [owned_client]})

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="rest_amount cannot exceed total_amount"):
        create_contract(session, owned_client.id, "100", "101")


# -------------------------
# update_contract
# -------------------------

def test_update_contract_ok_as_management(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    contract = update_contract(
        session=session,
        contract_id=1,
        total_amount="1500.00",
        rest_amount="750.00",
        is_signed=False,
    )

    assert contract.total_amount == Decimal("1500.00")
    assert contract.rest_amount == Decimal("750.00")
    assert contract.is_signed is False
    assert session.committed is True


def test_update_contract_ok_as_sales_owned(monkeypatch, sales_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)
    monkeypatch.setattr(
        "epicevents.services.contracts.has_permission",
        lambda role, action: action == CONTRACT_UPDATE_OWNED,
    )
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    contract = update_contract(
        session=session,
        contract_id=1,
        total_amount="1400.00",
        rest_amount="400.00",
        is_signed=True,
    )

    assert contract.total_amount == Decimal("1400.00")
    assert contract.rest_amount == Decimal("400.00")
    assert contract.is_signed is True
    assert session.committed is True


def test_update_contract_authentication_failed(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)

    with pytest.raises(Exception, match="Authentication failed"):
        update_contract(session, 1, total_amount="1500.00")


def test_update_contract_no_user(monkeypatch):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", raise_no_user)

    with pytest.raises(Exception, match="User no longer exists"):
        update_contract(session, 1, total_amount="1500.00")


def test_update_contract_no_permission(monkeypatch, fake_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: False)

    with pytest.raises(PermissionError, match="No permission"):
        update_contract(session, 1, total_amount="1500.00")


def test_update_contract_rejects_missing_contract_id(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)

    with pytest.raises(ValueError, match="contract_id is required"):
        update_contract(session, 0, total_amount="1500.00")


def test_update_contract_rejects_no_fields(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)

    with pytest.raises(ValueError, match="no fields to update"):
        update_contract(session, 1)


def test_update_contract_rejects_contract_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Contract: []})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: fake_user)

    with pytest.raises(ValueError, match="contract not found"):
        update_contract(session, 999, total_amount="1500.00")


def test_update_contract_rejects_not_owned_contract(monkeypatch, sales_user, unowned_contract):
    session = FakeSession(query_map={Contract: [unowned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)
    monkeypatch.setattr(
        "epicevents.services.contracts.has_permission",
        lambda role, action: action == CONTRACT_UPDATE_OWNED,
    )

    with pytest.raises(PermissionError, match="you are not the sales contact of this contract"):
        update_contract(session, 3, total_amount="1500.00")


def test_update_contract_rejects_client_not_found(monkeypatch, management_user, owned_contract):
    session = FakeSession(
        query_map={
            Contract: [owned_contract],
            Client: [],
        }
    )

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)

    with pytest.raises(ValueError, match="client not found"):
        update_contract(session, 1, client_id=999)


def test_update_contract_rejects_sales_changing_to_unowned_client(monkeypatch, sales_user, owned_contract, unowned_client):
    session = FakeSession(
        query_map={
            Contract: [owned_contract],
            Client: [unowned_client],
        }
    )

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)
    monkeypatch.setattr(
        "epicevents.services.contracts.has_permission",
        lambda role, action: action == CONTRACT_UPDATE_OWNED,
    )

    with pytest.raises(PermissionError, match="you are not the sales contact of this client"):
        update_contract(session, 1, client_id=unowned_client.id)


def test_update_contract_allows_sales_changing_to_owned_client(monkeypatch, sales_user, owned_contract, second_owned_client):
    session = FakeSession(
        query_map={
            Contract: [owned_contract],
            Client: [second_owned_client],
        }
    )

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: sales_user)
    monkeypatch.setattr(
        "epicevents.services.contracts.has_permission",
        lambda role, action: action == CONTRACT_UPDATE_OWNED,
    )

    contract = update_contract(session, 1, client_id=second_owned_client.id)

    assert contract.client_id == second_owned_client.id
    assert session.committed is True


def test_update_contract_rejects_invalid_total_amount(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)

    with pytest.raises(ValueError, match="total_amount must be a valid decimal amount"):
        update_contract(session, 1, total_amount="abc")


def test_update_contract_rejects_invalid_rest_amount(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)

    with pytest.raises(ValueError, match="rest_amount must be a valid decimal amount"):
        update_contract(session, 1, rest_amount="abc")


def test_update_contract_rejects_negative_total_amount(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="total_amount must be greater than or equal to 0"):
        update_contract(session, 1, total_amount="-1")


def test_update_contract_rejects_negative_rest_amount(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="rest_amount must be greater than or equal to 0"):
        update_contract(session, 1, rest_amount="-1")


def test_update_contract_rejects_rest_amount_exceeds_total_amount(monkeypatch, management_user, owned_contract):
    session = FakeSession(query_map={Contract: [owned_contract]})

    monkeypatch.setattr("epicevents.services.contracts.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.contracts.get_current_user", lambda: management_user)
    monkeypatch.setattr("epicevents.services.contracts.has_permission", lambda role, action: action == CONTRACT_UPDATE_ANY)
    monkeypatch.setattr(
        "epicevents.services.contracts._to_decimal",
        lambda value, field_name: Decimal(str(value)),
    )

    with pytest.raises(ValueError, match="rest_amount cannot exceed total_amount"):
        update_contract(session, 1, total_amount="100", rest_amount="101")