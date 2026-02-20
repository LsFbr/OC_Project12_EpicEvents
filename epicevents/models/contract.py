from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Boolean
from epicevents.models.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    rest_amount = Column(Numeric(10, 2), nullable=False)
    is_signed = Column(Boolean, nullable=False, default=False)
    created_time = Column(DateTime, nullable=False, default=datetime.now)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="contracts")
    events = relationship("Event", back_populates="contract")