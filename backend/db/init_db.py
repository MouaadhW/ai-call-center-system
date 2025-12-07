from db.database import engine, SessionLocal
from db.models import Base, Customer, Call, Ticket, Analytics
from loguru import logger
from datetime import datetime

def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Add sample data
        db = SessionLocal()
        
        # Check if data already exists
        existing_customers = db.query(Customer).count()
        if existing_customers > 0:
            logger.info("Database already contains data, skipping seed")
            db.close()
            return
        
        logger.info("Seeding database with sample data...")
        
        # Sample customers
        customers = [
            Customer(
                name="John Doe",
                phone="+1234567890",
                email="john@example.com",
                plan="Premium",
                balance=99.99,
                status="active"
            ),
            Customer(
                name="Jane Smith",
                phone="+1234567891",
                email="jane@example.com",
                plan="Standard",
                balance=49.99,
                status="active"
            ),
            Customer(
                name="Bob Johnson",
                phone="+1234567892",
                email="bob@example.com",
                plan="Basic",
                balance=29.99,
                status="active"
            ),
            Customer(
                name="Alice Williams",
                phone="+1234567893",
                email="alice@example.com",
                plan="Premium",
                balance=0.0,
                status="suspended"
            ),
            Customer(
                name="Charlie Brown",
                phone="+1234567894",
                email="charlie@example.com",
                plan="Standard",
                balance=49.99,
                status="active"
            )
        ]
        
        for customer in customers:
            db.add(customer)
        
        db.commit()
        logger.info(f"Added {len(customers)} sample customers")
        
        # Sample calls
        calls = [
            Call(
                customer_id=1,
                caller_number="+1234567890",
                duration=120,
                intent="billing",
                transcript="Customer: I want to check my bill\nAgent: Your balance is $99.99",
                resolution_status="resolved",
                status="completed"
            ),
            Call(
                customer_id=2,
                caller_number="+1234567891",
                duration=180,
                intent="technical_support",
                transcript="Customer: My internet is slow\nAgent: Created ticket #1",
                resolution_status="pending",
                status="completed"
            ),
            Call(
                customer_id=3,
                caller_number="+1234567892",
                duration=90,
                intent="account_info",
                transcript="Customer: What's my plan?\nAgent: You're on the Basic plan",
                resolution_status="resolved",
                status="completed"
            )
        ]
        
        for call in calls:
            db.add(call)
        
        db.commit()
        logger.info(f"Added {len(calls)} sample calls")
        
        # Sample tickets
        tickets = [
            Ticket(
                customer_id=2,
                type="technical_support",
                description="Customer reports slow internet connection",
                status="open",
                priority="normal"
            ),
            Ticket(
                customer_id=4,
                type="billing",
                description="Customer account suspended due to non-payment",
                status="in_progress",
                priority="high"
            )
        ]
        
        for ticket in tickets:
            db.add(ticket)
        
        db.commit()
        logger.info(f"Added {len(tickets)} sample tickets")
        
        # Sample analytics
        analytics = Analytics(
            date=datetime.now(),
            total_calls=3,
            answered_calls=3,
            missed_calls=0,
            avg_duration=130.0,
            total_tickets=2,
            resolved_tickets=0,
            top_intent="billing"
        )
        db.add(analytics)
        db.commit()
        logger.info("Added sample analytics data")
        
        db.close()
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()
