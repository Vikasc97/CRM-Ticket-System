from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.ticket_id"), index=True)
    field = Column(String)
    old_value = Column(String, nullable=True)
    new_value = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(String, unique=True, index=True)

    customer_name = Column(String)
    customer_email = Column(String)

    subject = Column(String)
    description = Column(Text)

    priority = Column(String, default="Medium")  # Low, Medium, High

    status = Column(String, default="Open")

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow)
