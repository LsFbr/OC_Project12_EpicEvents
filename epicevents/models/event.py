from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from epicevents.models.base import Base
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    notes = Column(Text, nullable=True)
    location = Column(String(128), nullable=False)
    attendees = Column(Integer, nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    support_contact_id = Column(Integer, ForeignKey("collaborators.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    support_contact = relationship("Collaborator", back_populates="events")
    contract = relationship("Contract", back_populates="events")