from sqlalchemy import Column, Integer, String, ForeignKey
from epicevents.models.base import Base
from sqlalchemy.orm import relationship

class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True)
    employee_number = Column(Integer, unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    full_name = Column(String(64), nullable=False)
    password_hash = Column(String(128), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="collaborators")
    clients = relationship("Client", back_populates="sales_contact")
    events = relationship("Event", back_populates="support_contact")