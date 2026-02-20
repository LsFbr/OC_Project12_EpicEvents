from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from epicevents.models.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    informations = Column(Text, nullable=True)
    name = Column(String(64), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    company_name = Column(String(64), nullable=False)
    created_time = Column(DateTime, nullable=False, default=datetime.now)
    last_update = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    sales_contact_id = Column(Integer, ForeignKey("collaborators.id"), nullable=False)
    sales_contact = relationship("Collaborator", back_populates="clients")
    contracts = relationship("Contract", back_populates="client")