from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100))
    plan = Column(String(50))
    balance = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    calls = relationship("Call", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.id}: {self.name}>"

class Call(Base):
    """Call record model"""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    caller_number = Column(String(20))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    duration = Column(Integer)  # in seconds
    intent = Column(String(50))
    transcript = Column(Text)
    resolution_status = Column(String(20))  # resolved, pending, escalated
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    recording_path = Column(String(255))
    
    # Relationships
    customer = relationship("Customer", back_populates="calls")
    
    def __repr__(self):
        return f"<Call {self.id}: {self.caller_number}>"

class Ticket(Base):
    """Support ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    type = Column(String(50))  # technical_support, billing, account, etc.
    description = Column(Text)
    status = Column(String(20), default="open")  # open, in_progress, resolved, closed
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    resolved_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    
    def __repr__(self):
        return f"<Ticket {self.id}: {self.type}>"

class Analytics(Base):
    """Analytics data model"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    total_calls = Column(Integer, default=0)
    answered_calls = Column(Integer, default=0)
    missed_calls = Column(Integer, default=0)
    avg_duration = Column(Float, default=0.0)
    total_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    top_intent = Column(String(50))
    
    def __repr__(self):
        return f"<Analytics {self.date}>"
