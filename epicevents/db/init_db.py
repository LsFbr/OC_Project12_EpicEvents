from epicevents.models.base import Base
from epicevents.db.session import engine

from epicevents.models.role import Role
from epicevents.models.collaborator import Collaborator

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized")

if __name__ == "__main__":
    init_db()