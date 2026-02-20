from sqlalchemy import Column, Integer, String
from epicevents.models.base import Base
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(24), unique=True, nullable=False)
    collaborators = relationship("Collaborator", back_populates="role")