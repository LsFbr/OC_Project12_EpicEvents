from epicevents.models.base import Base
from epicevents.db.session import engine, SessionLocal
from sqlalchemy import select
from epicevents.models.role import Role
from epicevents.models.collaborator import Collaborator
from epicevents.models.client import Client
from epicevents.models.contract import Contract
from epicevents.models.event import Event

ROLE_NAMES = ["SALES", "SUPPORT", "MANAGEMENT"]

def seed_roles(session):
    '''
    Seed the roles in the database
    Args:
        session: The session to use to seed the roles
    '''
    existing = set(
        session.scalars(
            select(Role.name).where(Role.name.in_(ROLE_NAMES))
        ).all()
    )

    for name in ROLE_NAMES:
        if name not in existing:
            session.add(Role(name=name))

    session.commit()

def init_db():
    '''
    Initialize the database
    '''
    Base.metadata.create_all(engine)
    print("Database initialized")

    session = SessionLocal()
    try:
        seed_roles(session)
        print("Roles seeded")
    finally:
        session.close()


if __name__ == "__main__":
    init_db()