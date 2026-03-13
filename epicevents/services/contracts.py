from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
from typing import Any

from epicevents.models.contract import Contract
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import (
    READ_ALL,
    CONTRACT_CREATE,
    CONTRACT_UPDATE_ANY,
    CONTRACT_UPDATE_OWNED,
    require_permission,
    has_permission,
)
from epicevents.auth.current_user import get_current_user
from epicevents.models.client import Client


def _to_decimal(value: Any, field_name: str) -> Decimal:
    if value is None or value == "":
        raise ValueError(f"{field_name} is required")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a valid decimal amount")


def get_all_contracts(session: Session) -> list[Contract]:
    require_authentication()

    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    result = session.execute(select(Contract))
    return result.scalars().all()


def create_contract(
    session: Session,
    client_id: int,
    total_amount: Any,
    rest_amount: Any,
    is_signed: bool = False,
) -> Contract:
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, CONTRACT_CREATE)

    if not client_id:
        raise ValueError("client_id is required")

    client = session.query(Client).filter(Client.id == client_id).one_or_none()
    if client is None:
        raise ValueError("client not found")

    total_amount = _to_decimal(total_amount, "total_amount")
    rest_amount = _to_decimal(rest_amount, "rest_amount")

    if total_amount < 0:
        raise ValueError("total_amount must be greater than or equal to 0")
    if rest_amount < 0:
        raise ValueError("rest_amount must be greater than or equal to 0")
    if rest_amount > total_amount:
        raise ValueError("rest_amount cannot exceed total_amount")

    contract = Contract(
        total_amount=total_amount,
        rest_amount=rest_amount,
        is_signed=bool(is_signed),
        client_id=client.id,
    )

    session.add(contract)
    session.commit()
    session.refresh(contract)
    return contract


def update_contract(
    session: Session,
    contract_id: int,
    **fields: Any,
) -> Contract:
    require_authentication()
    user = get_current_user()

    if not contract_id:
        raise ValueError("contract_id is required")
    if not fields:
        raise ValueError("no fields to update")

    contract = session.query(Contract).filter(Contract.id == contract_id).one_or_none()
    if contract is None:
        raise ValueError("contract not found")

    can_update_any = has_permission(user.role.name, CONTRACT_UPDATE_ANY)
    can_update_owned = has_permission(user.role.name, CONTRACT_UPDATE_OWNED)

    if can_update_any:
        pass
    elif can_update_owned:
        if contract.client.sales_contact_id != user.id:
            raise PermissionError("you are not the sales contact of this contract")
    else:
        raise PermissionError("No permission")

    if "client_id" in fields:
        client_id = fields["client_id"]
        if not client_id:
            raise ValueError("client_id is required")

        client = session.query(Client).filter(Client.id == client_id).one_or_none()
        if client is None:
            raise ValueError("client not found")

        if can_update_owned and client.sales_contact_id != user.id:
            raise PermissionError("you are not the sales contact of this client")

        contract.client_id = client.id

    new_total_amount = contract.total_amount
    new_rest_amount = contract.rest_amount

    if "total_amount" in fields:
        new_total_amount = _to_decimal(fields["total_amount"], "total_amount")
        if new_total_amount < 0:
            raise ValueError("total_amount must be greater than or equal to 0")

    if "rest_amount" in fields:
        new_rest_amount = _to_decimal(fields["rest_amount"], "rest_amount")
        if new_rest_amount < 0:
            raise ValueError("rest_amount must be greater than or equal to 0")

    if new_rest_amount > new_total_amount:
        raise ValueError("rest_amount cannot exceed total_amount")

    contract.total_amount = new_total_amount
    contract.rest_amount = new_rest_amount

    if "is_signed" in fields:
        contract.is_signed = bool(fields["is_signed"])

    session.commit()
    session.refresh(contract)
    return contract