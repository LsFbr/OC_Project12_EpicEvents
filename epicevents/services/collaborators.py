import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any

from epicevents.models.collaborator import Collaborator
from epicevents.models.role import Role
from epicevents.security.passwords import hash_password
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import READ_ALL, COLLAB_CREATE, COLLAB_UPDATE, COLLAB_DELETE, require_permission
from epicevents.auth.current_user import get_current_user


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def get_all_collaborators(session: Session) -> list[Collaborator]:
    
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    result = session.execute(select(Collaborator))
    return result.scalars().all()


def create_collaborator(
    session: Session,
    employee_number: str,
    full_name: str,
    email: str,
    role_name: str,
    plain_password: str,
) -> Collaborator:
    employee_number = (employee_number or "").strip()
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()
    role_name = (role_name or "").strip().upper()

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_CREATE)

    if not employee_number:
        raise ValueError("employee_number is required")
    if not full_name:
        raise ValueError("full_name is required")
    if not email or not _EMAIL_RE.match(email):
        raise ValueError("email is invalid")
    if len(plain_password or "") < 8:
        raise ValueError("password too short")

    role = session.query(Role).filter(Role.name == role_name).one_or_none()
    if role is None:
        raise ValueError("unknown role")

    if session.query(Collaborator).filter(Collaborator.email == email).first():
        raise ValueError("email already exists")

    if session.query(Collaborator).filter(Collaborator.employee_number == employee_number).first():
        raise ValueError("employee_number already exists")

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
    return collaborator


def update_collaborator(
    session: Session,
    employee_number: str,
    **fields: Any,
) -> Collaborator:
    employee_number = (employee_number or "").strip()
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_UPDATE)

    if not employee_number:
        raise ValueError("employee_number is required")
    if not fields:
        raise ValueError("no fields to update")

    collaborator = session.query(Collaborator).filter(Collaborator.employee_number == employee_number).one_or_none()
    if collaborator is None:
        raise ValueError("collaborator not found")

    if "full_name" in fields:
        full_name = (fields["full_name"] or "").strip()
        if not full_name:
            raise ValueError("full_name is required")
        collaborator.full_name = full_name

    if "email" in fields:
        email = (fields["email"] or "").strip().lower()
        if not email:
            raise ValueError("email is required")
        if not _EMAIL_RE.match(email):
            raise ValueError("email is invalid")
        existing = session.query(Collaborator).filter(Collaborator.email == email).one_or_none()
        if existing is not None and existing.id != collaborator.id:
            raise ValueError("email already exists")
        collaborator.email = email

    if "role_name" in fields:
        role_name = (fields["role_name"] or "").strip().upper()
        if not role_name:
            raise ValueError("role_name is required")
        role = session.query(Role).filter(Role.name == role_name).one_or_none()
        if role is None:
            raise ValueError("unknown role")

        collaborator.role_id = role.id

    if "plain_password" in fields:
        plain_password = (fields["plain_password"] or "").strip()
        if not plain_password:
            raise ValueError("password is required")
        if len(plain_password) < 8:
            raise ValueError("password too short")

        collaborator.password_hash = hash_password(plain_password)

    session.commit()
    session.refresh(collaborator)
    return collaborator


def delete_collaborator(
    session: Session,
    employee_number: str,
) -> None:
    employee_number = (employee_number or "").strip()

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, COLLAB_DELETE)

    if not employee_number:
        raise ValueError("employee_number is required")

    collaborator = (
        session.query(Collaborator)
        .filter(Collaborator.employee_number == employee_number)
        .one_or_none()
    )
    if collaborator is None:
        raise ValueError("collaborator not found")

    session.delete(collaborator)
    session.commit()