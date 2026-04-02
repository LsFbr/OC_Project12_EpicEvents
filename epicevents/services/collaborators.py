import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any

from epicevents.monitoring.sentry import capture_business_event
from epicevents.models.collaborator import Collaborator
from epicevents.models.role import Role
from epicevents.security.passwords import hash_password
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import READ_ALL, COLLAB_CREATE, COLLAB_UPDATE, COLLAB_DELETE, require_permission
from epicevents.auth.current_user import get_current_user
from epicevents.constants import PASSWORD_MIN_LENGTH
from epicevents.exceptions import BusinessValidationError


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_all_collaborators(session: Session) -> list[Collaborator]:

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    collaborators = session.execute(select(Collaborator))
    return collaborators.scalars().all()


def create_collaborator(
    session: Session,
    employee_number: int,
    full_name: str,
    email: str,
    role_name: str,
    plain_password: str,
) -> Collaborator:
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()
    role_name = (role_name or "").strip().upper()

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_CREATE)

    if employee_number is None:
        raise BusinessValidationError("employee_number is required")
    if not isinstance(employee_number, int):
        raise BusinessValidationError("employee_number must be an integer")

    if not full_name:
        raise BusinessValidationError("full_name is required")
    if len(full_name) > 64:
        raise BusinessValidationError("full_name must be less than 64 characters")

    if not email:
        raise BusinessValidationError("email is required")
    if len(email) > 128:
        raise BusinessValidationError("email must be less than 128 characters")
    if not _EMAIL_RE.match(email):
        raise BusinessValidationError("email is invalid")

    if not role_name:
        raise BusinessValidationError("role_name is required")

    if len(plain_password or "") < PASSWORD_MIN_LENGTH:
        raise BusinessValidationError("password too short")

    role = session.query(Role).filter(Role.name == role_name).one_or_none()
    if role is None:
        raise BusinessValidationError("unknown role")

    if session.query(Collaborator).filter(Collaborator.email == email).first():
        raise BusinessValidationError("email already exists")

    if session.query(Collaborator).filter(Collaborator.employee_number == employee_number).first():
        raise BusinessValidationError("employee_number already exists")

    collaborator = Collaborator(
        employee_number=employee_number,
        full_name=full_name,
        email=email,
        password_hash=hash_password(plain_password),
        role_id=role.id,
    )
    session.add(collaborator)
    session.commit()
    session.refresh(collaborator)

    capture_business_event(
        "collaborator_created",
        collaborator_id=collaborator.id,
        employee_number=collaborator.employee_number,
        role_name=role.name,
    )

    return collaborator


def update_collaborator(
    session: Session,
    employee_number: int,
    **fields: Any,
) -> Collaborator:
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_UPDATE)

    if employee_number is None:
        raise BusinessValidationError("employee_number is required")
    if not isinstance(employee_number, int):
        raise BusinessValidationError("employee_number must be an integer")
    if not fields:
        raise BusinessValidationError("no fields to update")

    collaborator = session.query(Collaborator).filter(Collaborator.employee_number == employee_number).one_or_none()
    if collaborator is None:
        raise BusinessValidationError("collaborator not found")

    if "full_name" in fields:
        full_name = (fields["full_name"] or "").strip()
        if not full_name:
            raise BusinessValidationError("full_name is required")
        if len(full_name) > 64:
            raise BusinessValidationError("full_name must be less than 64 characters")
        collaborator.full_name = full_name

    if "email" in fields:
        email = (fields["email"] or "").strip().lower()
        if not email:
            raise BusinessValidationError("email is required")
        if not _EMAIL_RE.match(email):
            raise BusinessValidationError("email is invalid")
        if len(email) > 128:
            raise BusinessValidationError("email must be less than 128 characters")
        existing = session.query(Collaborator).filter(Collaborator.email == email).one_or_none()
        if existing is not None and existing.id != collaborator.id:
            raise BusinessValidationError("email already exists")
        collaborator.email = email

    if "role_name" in fields:
        role_name = (fields["role_name"] or "").strip().upper()
        if not role_name:
            raise BusinessValidationError("role_name is required")
        role = session.query(Role).filter(Role.name == role_name).one_or_none()
        if role is None:
            raise BusinessValidationError("unknown role")

        collaborator.role_id = role.id

    if "plain_password" in fields:
        plain_password = (fields["plain_password"] or "").strip()
        if not plain_password:
            raise BusinessValidationError("password is required")
        if len(plain_password) < PASSWORD_MIN_LENGTH:
            raise BusinessValidationError("password too short")

        collaborator.password_hash = hash_password(plain_password)

    session.commit()
    session.refresh(collaborator)

    capture_business_event(
        "collaborator_updated",
        collaborator_id=collaborator.id,
        employee_number=collaborator.employee_number,
        updated_fields=sorted(fields.keys()),
    )

    return collaborator


def delete_collaborator(
    session: Session,
    employee_number: int,
) -> Collaborator:

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_DELETE)

    if employee_number is None:
        raise BusinessValidationError("employee_number is required")
    if not isinstance(employee_number, int):
        raise BusinessValidationError("employee_number must be an integer")

    collaborator = (
        session.query(Collaborator)
        .filter(Collaborator.employee_number == employee_number)
        .one_or_none()
    )
    if collaborator is None:
        raise BusinessValidationError("collaborator not found")

    session.delete(collaborator)
    session.commit()

    capture_business_event(
        "collaborator_deleted",
        collaborator_id=collaborator.id,
        employee_number=collaborator.employee_number,
    )

    return collaborator
