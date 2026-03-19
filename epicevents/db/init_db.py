from epicevents.models.base import Base
from epicevents.db.session import engine, SessionLocal
from sqlalchemy import select
from epicevents.models.role import Role
from epicevents.models.collaborator import Collaborator
from epicevents.security.passwords import hash_password
import os
from epicevents.constants import ROLE_NAMES

def seed_roles(session):
    """
    Seed the roles in the database.
    """
    existing = set(
        session.scalars(
            select(Role.name).where(Role.name.in_(ROLE_NAMES))
        ).all()
    )

    for name in ROLE_NAMES:
        if name not in existing:
            session.add(Role(name=name))

    session.commit()


def seed_initial_management(session):
    """
    Seed the initial MANAGEMENT collaborator if it does not already exist.
    """
    raw_employee_number = os.getenv("BOOTSTRAP_MANAGEMENT_EMPLOYEE_NUMBER")
    full_name = os.getenv("BOOTSTRAP_MANAGEMENT_FULL_NAME")
    email = os.getenv("BOOTSTRAP_MANAGEMENT_EMAIL")
    password = os.getenv("BOOTSTRAP_MANAGEMENT_PASSWORD")

    if not all([raw_employee_number, full_name, email, password]):
        raise ValueError("Missing bootstrap management environment variables.")

    try:
        employee_number = int(raw_employee_number)
    except ValueError as exc:
        raise ValueError(
            "BOOTSTRAP_MANAGEMENT_EMPLOYEE_NUMBER must be an integer."
        ) from exc

    management_role = session.execute(
        select(Role).where(Role.name == "MANAGEMENT")
    ).scalar_one_or_none()

    if management_role is None:
        raise ValueError("MANAGEMENT role not found in database.")

    existing = session.execute(
        select(Collaborator).where(
            Collaborator.employee_number == employee_number
        )
    ).scalar_one_or_none()

    if existing is None:
        collaborator = Collaborator(
            employee_number=employee_number,
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role_id=management_role.id,
        )
        session.add(collaborator)
        session.commit()
        print("Initial MANAGEMENT collaborator created.")
    else:
        print("Initial MANAGEMENT collaborator already exists.")


def init_db():
    """
    Initialize the database.
    """
    Base.metadata.create_all(engine)
    print("Database initialized")

    session = SessionLocal()
    try:
        seed_roles(session)
        print("Roles seeded")

        seed_initial_management(session)
        print("Initial management user seeded")
    finally:
        session.close()


if __name__ == "__main__":
    init_db()