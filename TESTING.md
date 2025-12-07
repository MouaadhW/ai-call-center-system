# 🧪 Testing Guide

Comprehensive testing procedures for the AI Call Center System.

## Table of Contents

1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [End-to-End Testing](#end-to-end-testing)
4. [Performance Testing](#performance-testing)
5. [Test Scenarios](#test-scenarios)

---

## 🔬 Unit Testing

### Backend Components

```bash
# Install test dependencies
cd backend
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_agent.py -v
```

### Test ASR Engine

```bash
docker exec -it backend python -c "
from asr.whisper_engine import WhisperASR
import numpy as np

asr = WhisperASR()
# Test with sample audio
audio = np.random.randn(16000)  # 1 second of random audio
result = asr.transcribe(audio)
print(f'Transcription: {result}')
"
```

### Test TTS Engine

```bash
docker exec -it backend python -c "
from tts.tts_engine import PiperTTS

tts = PiperTTS()
audio = tts.synthesize('Hello, this is a test.')
print(f'Generated audio length: {len(audio)} samples')
"
```

### Test Intent Classifier

```bash
docker exec -it backend python -c "
from agent.intent_classifier import IntentClassifier

classifier = IntentClassifier()
intent = classifier.classify('My internet is very slow')
print(f'Detected intent: {intent}')
"
```

---

## 🔗 Integration Testing

### Test Asterisk AGI Connection

```bash
# Check AGI is listening
docker exec -it backend netstat -tuln | grep 4573

# Test AGI handler
docker exec -it backend python -c "
from agi.agi_handler import AGIServer
print('AGI Server initialized successfully')
"
```

### Test Database Operations

```bash
docker exec -it backend python -c "
from db.database import SessionLocal
from db.models import Customer, Call, Ticket

db = SessionLocal()

# Create test customer
customer = Customer(
    name='Test User',
    phone='+1111111111',
    plan='Basic',
    balance=50.0,
    status='active'
)
db.add(customer)
db.commit()

# Create test call
call = Call(
    customer_id=customer.id,
    duration=120,
    intent='billing',
    resolution_status='resolved'
)
db.add(call)
db.commit()

print(f'Created customer ID: {customer.id}')
print(f'Created call ID: {call.id}')

# Cleanup
db.delete(call)
db.delete(customer)
db.commit()
db.close()
"
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all calls
curl http://localhost:8000/api/calls

# Get analytics
curl http://localhost:8000/api/analytics

# Get specific customer
curl http://localhost:8000/api/customers/1

# Create test call record
curl -X POST http://localhost:8000/api/calls \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "duration": 180,
    "intent": "technical_support",
    "transcript": "Customer reported slow internet",
    "resolution_status": "pending"
  }'
```

---

## 🎬 End-to-End Testing

### Test Complete Call Flow

#### 1. Setup Test Environment

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Initialize test data
docker exec -it backend python scripts/seed_test_data.py
```

#### 2. Test with SIP Softphone

**Install Softphone**
- Linux: `sudo apt install linphone`
- macOS: `brew install --cask zoiper`
- Windows: Download Zoiper from zoiper.com

**Configure Softphone**
```
Account Name: Test Account
SIP Server: localhost
Port: 5060
Username: 6001
Password: 6001
Transport: UDP
```

**Register & Test**
1. Register the account
2. Call extension **100**
3. Speak clearly: "I want to check my bill"
4. Verify AI responds appropriately

#### 3. Automated E2E Test Script

```bash
python scripts/test_call.py
```

Expected Output:
```
✓ Connecting to Asterisk...
✓ Initiating call to extension 100...
✓ Call connected
✓ Playing test audio...
✓ Receiving AI response...
✓ Transcription: "Hello! Welcome to AI Call Center..."
✓ Call completed successfully
✓ Duration: 45 seconds
✓ Intent detected: greeting
✓ Test PASSED
```

---

## ⚡ Performance Testing

### Load Testing with Multiple Concurrent Calls

```bash
# Install load testing tool
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

### Load Test Configuration

```python
# tests/load_test.py
from locust import HttpUser, task, between

class CallCenterUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_calls(self):
        self.client.get("/api/calls")
    
    @task
    def get_analytics(self):
        self.client.get("/api/analytics")
```

### Measure Response Times

```bash
# Test ASR latency
docker exec -it backend python -c "
import time
from asr.whisper_engine import WhisperASR
import numpy as np

asr = WhisperASR()
audio = np.random.randn(16000 * 5)  # 5 seconds

start = time.time()
result = asr.transcribe(audio)
latency = time.time() - start

print(f'ASR Latency: {latency:.2f}s')
print(f'Real-time factor: {latency / 5:.2f}x')
"
```

### Monitor Resource Usage

```bash
# Check container stats
docker stats
```

Expected usage:
- asterisk: ~50MB RAM, <5% CPU
- backend: ~500MB RAM, 10-30% CPU
- dashboard: ~100MB RAM, <5% CPU

---

## 📋 Test Scenarios

### Scenario 1: Billing Inquiry (Happy Path)

**Steps:**
1. Call extension 100
2. Say: "I want to check my bill"
3. Provide customer ID: "12345"
4. Listen to balance information

**Expected Result:**
- AI greets caller
- AI asks for customer ID
- AI retrieves and reads balance
- Call ends gracefully

**Verification:**

```bash
# Check call was logged
curl http://localhost:8000/api/calls | jq '.[-1]'
```

Should show:
- intent: "billing"
- resolution_status: "resolved"
- duration: ~30-60 seconds

---

### Scenario 2: Technical Support (Ticket Creation)

**Steps:**
1. Call extension 100
2. Say: "My internet is not working"
3. Provide customer ID
4. Describe issue: "No connection since morning"

**Expected Result:**
- AI collects problem details
- AI creates support ticket
- AI provides ticket number
- Call logged with transcript

**Verification:**

```bash
# Check ticket was created
docker exec -it backend python -c "
from db.database import SessionLocal
from db.models import Ticket

db = SessionLocal()
ticket = db.query(Ticket).order_by(Ticket.id.desc()).first()
print(f'Ticket #{ticket.id}: {ticket.description}')
print(f'Status: {ticket.status}')
"
```

---

### Scenario 3: Invalid Customer ID

**Steps:**
1. Call extension 100
2. Say: "Check my bill"
3. Provide invalid ID: "99999"

**Expected Result:**
- AI asks for customer ID
- AI reports ID not found
- AI offers to transfer to human agent
- Call logged as "unresolved"

---

### Scenario 4: Multiple Intent Changes

**Steps:**
1. Call extension 100
2. Say: "I want to check my bill"
3. Then say: "Actually, my internet is slow"
4. Then say: "Never mind, just the bill please"

**Expected Result:**
- AI handles context switching
- AI maintains conversation flow
- Final intent: "billing"
- Call logged with full transcript

---

### Scenario 5: Silence/No Response

**Steps:**
1. Call extension 100
2. Stay silent for 10 seconds

**Expected Result:**
- AI prompts: "Are you still there?"
- After 20 seconds: "I'll transfer you to an agent"
- Call logged as "no_response"

---

## 🐛 Debugging Failed Tests

### Enable Debug Logging

Edit `.env`:

```env
LOG_LEVEL=DEBUG
```

Restart:

```bash
docker-compose restart backend
```

View logs:

```bash
docker-compose logs -f backend
```

### Check Asterisk Dialplan

```bash
docker exec -it asterisk asterisk -rx "dialplan show from-internal"
```

### Verify AGI Communication

```bash
# Enable AGI debug
docker exec -it asterisk asterisk -rx "agi set debug on"

# Make test call and watch logs
docker logs -f asterisk
```

### Test Database Connectivity

```bash
docker exec -it backend python -c "
from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection: OK')
"
```

---

## ✅ Test Checklist

Before deploying to production:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E test scenarios complete successfully
- [ ] Load test shows acceptable performance (<2s response time)
- [ ] No memory leaks (run for 1 hour, check memory usage)
- [ ] All API endpoints return correct status codes
- [ ] Dashboard loads and displays data correctly
- [ ] Asterisk registers SIP endpoints
- [ ] AGI handler responds to calls
- [ ] Database operations complete without errors
- [ ] Logs show no critical errors
- [ ] Call recordings are saved correctly
- [ ] Analytics data is accurate

---

## 📊 Test Reports

Generate test report:

```bash
pytest --html=report.html --self-contained-html
```

View coverage:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

Need help with testing? Open an issue with:
- Test scenario description
- Expected vs actual behavior
- Relevant logs
- System configuration
