from typing import Any
import re
from sqlalchemy import select
from sqlalchemy.orm import Session

from epicevents.models.client import Client
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import READ_ALL, CLIENT_CREATE, CLIENT_UPDATE_OWNED, require_permission
from epicevents.auth.current_user import get_current_user
from epicevents.exceptions import BusinessValidationError, BusinessAuthorizationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_PHONE_RE = re.compile(r"^\+?[0-9][0-9 .()-]*$")


def get_all_clients(session: Session) -> list[Client]:

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    result = session.execute(select(Client))
    return result.scalars().all()

def create_client(
    session: Session,
    informations: str,
    name: str,
    email: str,
    phone_number: str,
    company_name: str,
) -> Client:
    informations = (informations or "").strip()
    name = (name or "").strip()
    email = (email or "").strip().lower()
    phone_number = (phone_number or "").strip()
    company_name = (company_name or "").strip()

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, CLIENT_CREATE)

    if not name:
        raise BusinessValidationError("name is required")
    if not email:
        raise BusinessValidationError("email is required")
    if not _EMAIL_RE.match(email):
        raise BusinessValidationError("email is invalid")
    if not phone_number:
        raise BusinessValidationError("phone_number is required")
    if not _PHONE_RE.match(phone_number):
        raise BusinessValidationError("phone_number is invalid")
    if not company_name:
        raise BusinessValidationError("company_name is required")

    if session.query(Client).filter(Client.email == email).first():
        raise BusinessValidationError("email already exists")

    client = Client(
        informations=informations,
        name=name,
        email=email,
        phone_number=phone_number,
        company_name=company_name,
        sales_contact_id=user.id,
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

def update_client(
    session: Session,
    client_id: int,
    **fields: Any,
) -> Client:
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, CLIENT_UPDATE_OWNED)

    if not client_id:
        raise BusinessValidationError("client_id is required")
    if not fields:
        raise BusinessValidationError("no fields to update")

    client = session.query(Client).filter(Client.id == client_id).one_or_none()
    if client is None:
        raise BusinessValidationError("client not found")

    if client.sales_contact_id != user.id:
        raise BusinessAuthorizationError("You are not the sales contact of this client")

    if "informations" in fields:
        informations = (fields["informations"] or "").strip()
        client.informations = informations

    if "name" in fields:
        name = (fields["name"] or "").strip()
        if not name:
            raise BusinessValidationError("name is required")
        client.name = name

    if "email" in fields:
        email = (fields["email"] or "").strip().lower()
        if not email:
            raise BusinessValidationError("email is required")
        if not _EMAIL_RE.match(email):
            raise BusinessValidationError("email is invalid")
        existing = session.query(Client).filter(Client.email == email).one_or_none()
        if existing is not None and existing.id != client.id:
            raise BusinessValidationError("email already exists")
        client.email = email

    if "phone_number" in fields:
        phone_number = (fields["phone_number"] or "").strip()
        if not phone_number:
            raise BusinessValidationError("phone_number is required")
        if not _PHONE_RE.match(phone_number):
            raise BusinessValidationError("phone_number is invalid")
        client.phone_number = phone_number

    if "company_name" in fields:
        company_name = (fields["company_name"] or "").strip()
        if not company_name:
            raise BusinessValidationError("company_name is required")
        client.company_name = company_name

    session.commit()
    session.refresh(client)
    return client
