# ⚡ Quick Start Guide

Get your AI Call Center running in 5 minutes!

## Prerequisites Check

```bash
# Verify Docker
docker --version
# Should show: Docker version 20.10+

# Verify Docker Compose
docker-compose --version
# Should show: Docker Compose version 2.0+

# Verify ports are free
sudo lsof -i :5060  # Should be empty
sudo lsof -i :8000  # Should be empty
sudo lsof -i :3000  # Should be empty
```

---

## 🚀 5-Minute Setup

### 1. Clone & Configure (1 min)

```bash
git clone https://github.com/MouaadhW/ai-call-center-system.git
cd ai-call-center-system
cp .env.example .env
```

### 2. Start Services (2 min)

```bash
docker-compose up -d
```

Wait for containers to start:

```bash
docker-compose ps
```

### 3. Initialize Database (30 sec)

```bash
docker exec -it backend python -m db.init_db
```

### 4. Verify Everything Works (1 min)

```bash
# Check Asterisk
docker exec -it asterisk asterisk -rx "core show version"

# Check Backend
curl http://localhost:8000/health

# Check Dashboard
open http://localhost:3000
```

### 5. Make Test Call (30 sec)

**Option A: Using Softphone**
- Install Zoiper or Linphone
- Configure:
  - Server: localhost:5060
  - User: 6001
  - Pass: 6001
- Call extension **100**

**Option B: Using Test Script**

```bash
python scripts/test_call.py
```

---

## 🎉 You're Done!

Your AI Call Center is now running:

- 📞 **Asterisk PBX**: localhost:5060
- 🔌 **Backend API**: http://localhost:8000
- 📊 **Dashboard**: http://localhost:3000

---

## 🔧 Quick Configuration

### Add a New Customer

```bash
docker exec -it backend python -c "
from db.database import SessionLocal
from db.models import Customer

db = SessionLocal()
customer = Customer(
    name='John Doe',
    phone='+1234567890',
    plan='Premium',
    balance=100.0,
    status='active'
)
db.add(customer)
db.commit()
print('Customer added!')
"
```

### Customize AI Responses

Edit `backend/knowledge/company_kb.json`:

```json
{
  "greeting": "Hello! Welcome to AI Call Center. How can I help you today?",
  "intents": {
    "billing": {
      "keywords": ["bill", "payment", "invoice", "charge"],
      "response": "Let me check your billing information..."
    }
  }
}
```

Restart backend:

```bash
docker-compose restart backend
```

---

## 📱 Test Scenarios

### Scenario 1: Billing Inquiry
1. Call **100**
2. Say: "I want to check my bill"
3. Provide customer ID when asked
4. AI will fetch and read your balance

### Scenario 2: Technical Support
1. Call **100**
2. Say: "My internet is slow"
3. AI will troubleshoot and create a ticket

### Scenario 3: New Service Request
1. Call **100**
2. Say: "I need a new SIM card"
3. AI will collect details and create order

---

## 🛑 Stop Services

```bash
docker-compose down
```

## 🔄 Restart Services

```bash
docker-compose restart
```

## 📋 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f asterisk
```

---

## ⚠️ Common Issues

### "Port 5060 already in use"

```bash
sudo lsof -i :5060
sudo kill -9 <PID>
```

### "Backend won't start"

```bash
docker-compose logs backend
# Usually missing dependencies - rebuild:
docker-compose build backend
docker-compose up -d backend
```

### "Can't register softphone"

```bash
# Check Asterisk is running
docker exec -it asterisk asterisk -rx "pjsip show endpoints"
# Should show endpoint 6001
```

---

## 🎯 Next Steps

- Read [INSTALLATION.md](INSTALLATION.md) for detailed configuration
- Read [TESTING.md](TESTING.md) for comprehensive testing
- Customize knowledge base
- Add more SIP endpoints
- Configure real SIP trunk for production

---

Questions? Check the main [README.md](README.md) or open an issue!
