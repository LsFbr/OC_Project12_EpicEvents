import re
from sqlalchemy.orm import Session

from epicevents.models.collaborator import Collaborator
from epicevents.models.role import Role
from epicevents.security.passwords import hash_password

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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