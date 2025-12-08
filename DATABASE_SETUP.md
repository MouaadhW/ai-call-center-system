# 🗄️ Database Setup Guide

This guide will help you initialize and set up the database for the AI Call Center system.

---

## 🚀 Quick Setup (One Command)

```bash
docker exec backend python -m db.init_db
```

That's it! This will:
- Create all database tables
- Add sample customers (IDs: 1, 2, 3, 4, 5)
- Add sample calls and tickets
- Set up analytics data

---

## 📋 Step-by-Step Setup

### Step 1: Make sure Docker services are running

```bash
# Check if backend container is running
docker ps | findstr backend

# If not running, start it:
docker-compose up -d backend
```

### Step 2: Initialize the database

```bash
# Initialize database with sample data
docker exec backend python -m db.init_db
```

**Expected Output:**
```
Creating database tables...
Database tables created successfully
Seeding database with sample data...
Added 5 sample customers
Added 3 sample calls
Added 2 sample tickets
Added sample analytics data
Database initialization complete!
```

### Step 3: Verify database was created

```bash
# Check if database file exists
docker exec backend ls -la data/callcenter.db

# Or check via Python
docker exec backend python -c "from db.database import SessionLocal; from db.models import Customer; db = SessionLocal(); print(f'Customers: {db.query(Customer).count()}'); db.close()"
```

---

## 👥 Sample Customers Created

After initialization, you'll have these test customers:

| ID | Name | Phone | Plan | Balance | Status |
|----|------|-------|------|---------|--------|
| 1 | John Doe | +1234567890 | Premium | $99.99 | active |
| 2 | Jane Smith | +1234567891 | Standard | $49.99 | active |
| 3 | Bob Johnson | +1234567892 | Basic | $29.99 | active |
| 4 | Alice Williams | +1234567893 | Premium | $0.00 | suspended |
| 5 | Charlie Brown | +1234567894 | Standard | $49.99 | active |

**You can use these IDs to test the system!**

---

## 🧪 Testing with Sample Data

### Test Billing:
1. Open voice interface: `http://localhost:8004`
2. Say: "I want to check my bill"
3. When asked for ID, say: "1" or "My ID is 1"
4. AI should respond with John Doe's billing info

### Test Account Info:
1. Say: "Can you tell me about my account?"
2. Provide ID: "2"
3. AI should show Jane Smith's account details

### Test Technical Support:
1. Say: "My internet is slow"
2. Provide ID: "3"
3. AI should create a support ticket

---

## 🔧 Troubleshooting

### Issue: "No such table: customers"

**Solution:**
```bash
# Reinitialize the database
docker exec backend python -m db.init_db
```

### Issue: "Database is locked"

**Solution:**
```bash
# Stop all services
docker-compose down

# Remove old database (WARNING: This deletes all data!)
docker exec backend rm -f data/callcenter.db

# Restart and reinitialize
docker-compose up -d
docker exec backend python -m db.init_db
```

### Issue: "Database already contains data"

**Solution:**
This is normal! The init script won't overwrite existing data. If you want to reset:

```bash
# Remove database file
docker exec backend rm -f data/callcenter.db

# Reinitialize
docker exec backend python -m db.init_db
```

### Issue: "Permission denied"

**Solution:**
```bash
# Make sure backend container has write permissions
docker exec backend chmod -R 777 data/
docker exec backend python -m db.init_db
```

---

## 📊 Database Location

The database file is located at:
```
backend/data/callcenter.db
```

Inside the Docker container, the full path is:
```
/backend/data/callcenter.db
```

---

## 🔍 Verify Database Contents

### Check customers:
```bash
docker exec backend python -c "
from db.database import SessionLocal
from db.models import Customer
db = SessionLocal()
customers = db.query(Customer).all()
for c in customers:
    print(f'ID: {c.id}, Name: {c.name}, Balance: \${c.balance}')
db.close()
"
```

### Check calls:
```bash
docker exec backend python -c "
from db.database import SessionLocal
from db.models import Call
db = SessionLocal()
calls = db.query(Call).all()
print(f'Total calls: {len(calls)}')
db.close()
"
```

### Check tickets:
```bash
docker exec backend python -c "
from db.database import SessionLocal
from db.models import Ticket
db = SessionLocal()
tickets = db.query(Ticket).all()
print(f'Total tickets: {len(tickets)}')
db.close()
"
```

---

## 🔄 Reset Database (Fresh Start)

If you want to completely reset the database:

```bash
# Stop services
docker-compose down

# Remove database file
docker exec backend rm -f data/callcenter.db 2>/dev/null || echo "Database already removed"

# Or remove from host if container is stopped
rm -f backend/data/callcenter.db

# Restart services
docker-compose up -d

# Reinitialize
docker exec backend python -m db.init_db
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Database file exists: `backend/data/callcenter.db`
- [ ] 5 customers created (check with query above)
- [ ] 3 sample calls created
- [ ] 2 sample tickets created
- [ ] Can query customers via API: `curl http://localhost:8000/api/customers`
- [ ] Voice interface can access customer data

---

## 🎯 Next Steps

After database setup:

1. **Start voice interface**: `docker exec -d backend python voiceproduction.py`
2. **Test with sample customers**: Use IDs 1-5
3. **View dashboard**: `http://localhost:3000` to see calls and analytics

---

## 📝 Database Schema

The database contains these tables:

- **customers**: Customer information (name, phone, plan, balance, status)
- **calls**: Call records (caller, duration, transcript, intent, status)
- **tickets**: Support tickets (type, description, status, priority)
- **analytics**: Analytics data (call counts, averages, etc.)

---

**Need Help?** Check the logs:
```bash
docker exec backend tail -f logs/callcenter.log
```

