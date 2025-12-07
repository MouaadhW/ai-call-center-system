from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db.models import Customer, Call, Ticket, Analytics
from datetime import datetime, timedelta
from loguru import logger

router = APIRouter()

# ============================================
# CUSTOMER ENDPOINTS
# ============================================

@router.get("/customers")
async def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/customers/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers")
async def create_customer(customer_data: dict, db: Session = Depends(get_db)):
    """Create new customer"""
    try:
        customer = Customer(**customer_data)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================
# CALL ENDPOINTS
# ============================================

@router.get("/calls")
async def get_calls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all calls"""
    calls = db.query(Call).order_by(Call.start_time.desc()).offset(skip).limit(limit).all()
    return calls

@router.get("/calls/{call_id}")
async def get_call(call_id: int, db: Session = Depends(get_db)):
    """Get call by ID"""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@router.post("/calls")
async def create_call(call_data: dict, db: Session = Depends(get_db)):
    """Create new call record"""
    try:
        call = Call(**call_data)
        db.add(call)
        db.commit()
        db.refresh(call)
        return call
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/calls/customer/{customer_id}")
async def get_customer_calls(customer_id: int, db: Session = Depends(get_db)):
    """Get all calls for a customer"""
    calls = db.query(Call).filter(Call.customer_id == customer_id).order_by(Call.start_time.desc()).all()
    return calls

# ============================================
# TICKET ENDPOINTS
# ============================================

@router.get("/tickets")
async def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tickets"""
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return tickets

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get ticket by ID"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/tickets")
async def create_ticket(ticket_data: dict, db: Session = Depends(get_db)):
    """Create new ticket"""
    try:
        ticket = Ticket(**ticket_data)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/tickets/{ticket_id}")
async def update_ticket(ticket_id: int, ticket_data: dict, db: Session = Depends(get_db)):
    """Update ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    for key, value in ticket_data.items():
        setattr(ticket, key, value)
    
    ticket.updated_at = datetime.now()
    db.commit()
    db.refresh(ticket)
    return ticket

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics summary"""
    try:
        # Total calls
        total_calls = db.query(Call).count()
        answered_calls = db.query(Call).filter(Call.status == "completed").count()
        
        # Average duration
        from sqlalchemy import func
        avg_duration = db.query(func.avg(Call.duration)).filter(Call.duration.isnot(None)).scalar() or 0
        
        # Calls by intent
        intent_counts = db.query(
            Call.intent,
            func.count(Call.id).label('count')
        ).filter(Call.intent.isnot(None)).group_by(Call.intent).all()
        
        intents = {intent: count for intent, count in intent_counts}
        
        # Recent calls (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_calls = db.query(Call).filter(Call.start_time >= yesterday).count()
        
        # Tickets
        total_tickets = db.query(Ticket).count()
        open_tickets = db.query(Ticket).filter(Ticket.status == "open").count()
        resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved").count()
        
        # Top issues
        ticket_types = db.query(
            Ticket.type,
            func.count(Ticket.id).label('count')
        ).group_by(Ticket.type).all()
        
        top_issues = {ticket_type: count for ticket_type, count in ticket_types}
        
        return {
            "total_calls": total_calls,
            "answered_calls": answered_calls,
            "missed_calls": total_calls - answered_calls,
            "avg_duration": round(avg_duration, 2),
            "recent_calls_24h": recent_calls,
            "intents": intents,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_tickets": resolved_tickets,
            "top_issues": top_issues
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/daily")
async def get_daily_analytics(days: int = 7, db: Session = Depends(get_db)):
    """Get daily analytics for the last N days"""
    try:
        from sqlalchemy import func, cast, Date
        
        start_date = datetime.now() - timedelta(days=days)
        
        daily_stats = db.query(
            cast(Call.start_time, Date).label('date'),
            func.count(Call.id).label('total_calls'),
            func.avg(Call.duration).label('avg_duration')
        ).filter(
            Call.start_time >= start_date
        ).group_by(
            cast(Call.start_time, Date)
        ).all()
        
        result = []
        for stat in daily_stats:
            result.append({
                "date": stat.date.isoformat(),
                "total_calls": stat.total_calls,
                "avg_duration": round(stat.avg_duration or 0, 2)
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting daily analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/intents")
async def get_intent_analytics(db: Session = Depends(get_db)):
    """Get intent distribution"""
    try:
        from sqlalchemy import func
        
        intent_stats = db.query(
            Call.intent,
            func.count(Call.id).label('count'),
            func.avg(Call.duration).label('avg_duration')
        ).filter(
            Call.intent.isnot(None)
        ).group_by(Call.intent).all()
        
        result = []
        for stat in intent_stats:
            result.append({
                "intent": stat.intent,
                "count": stat.count,
                "avg_duration": round(stat.avg_duration or 0, 2)
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting intent analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
