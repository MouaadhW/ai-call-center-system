# 🚀 Complete Testing Guide - AI Call Center System

This guide provides step-by-step instructions to test your AI call center system from scratch.

## Quick Start

Run the automated test script:
```bash
fulltest.bat
```

This will test all components automatically. Follow the manual steps below for detailed testing.

---

## Phase 1: Initial Setup & Verification

### Step 1: Clean Start

```bash
# Navigate to project directory
cd C:\path\to\ai-call-center-system

# Stop everything
docker-compose down -v

# Remove old containers and volumes (optional)
docker system prune -a --volumes
# Type 'y' to confirm

# Verify everything is stopped
docker ps -a
```

### Step 2: Build Everything Fresh

```bash
# Build all containers (takes 5-10 minutes)
docker-compose build --no-cache

# Expected output:
# Successfully built [container-id]
# Successfully tagged ai-call-center-system-asterisk:latest
# Successfully tagged ai-call-center-system-backend:latest
# Successfully tagged ai-call-center-system-dashboard:latest
```

### Step 3: Start All Services

```bash
# Start in detached mode
docker-compose up -d

# Wait 15 seconds for services to initialize
timeout /t 15

# Check status
docker-compose ps
```

**Expected output:**
```
NAME        IMAGE                              STATUS        PORTS
asterisk    ai-call-center-system-asterisk     Up            0.0.0.0:5060->5060/tcp, udp
backend     ai-call-center-system-backend      Up            0.0.0.0:8000->8000/tcp
dashboard   ai-call-center-system-dashboard    Up            0.0.0.0:3000->3000/tcp
```

All should show **"Up"** status!

### Step 4: Initialize Database

```bash
# Initialize database with sample data
docker exec backend python -m db.init_db
```

**Expected output:**
```
INFO: Creating database tables...
INFO: Database tables created successfully
INFO: Seeding database with sample data...
INFO: Added 5 sample customers
INFO: Added 3 sample calls
INFO: Added 2 sample tickets
INFO: Database initialization completed successfully
```

---

## Phase 2: Component Testing

### Test 1: Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy","version":"1.0.0"}
```

```bash
# Test analytics endpoint
curl http://localhost:8000/api/analytics
```

**Expected output:**
```json
{
  "totalcalls": 3,
  "answeredcalls": 3,
  "missedcalls": 0,
  "avgduration": 130.0,
  ...
}
```

✅ **If both work, Backend is OK!**

### Test 2: Dashboard

1. Open browser: `http://localhost:3000`
2. Expected:
   - Dashboard loads
   - Shows statistics (Total Calls, Answered Calls, etc.)
   - Shows charts and tables

✅ **If dashboard loads, Frontend is OK!**

### Test 3: Asterisk SIP Server

```bash
# Check Asterisk version
docker exec asterisk asterisk -rx "core show version"

# Check SIP endpoints
docker exec asterisk asterisk -rx "pjsip show endpoints"
```

**Expected output:**
```
Endpoint:  6001/6001                                             Not in use    0 of 10
Endpoint:  6002/6002                                             Not in use    0 of 10
Endpoint:  6003/6003                                             Not in use    0 of 10
```

```bash
# Check SIP transports
docker exec asterisk asterisk -rx "pjsip show transports"
```

**Expected output:**
```
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-tcp             tcp      0      0  0.0.0.0:5060
```

✅ **If all show correctly, Asterisk is OK!**

### Test 4: AGI Connection

```bash
# Test AGI server from Asterisk
docker exec asterisk nc -v backend 4573
```

**Expected output:**
```
Connection to backend 4573 port [tcp/] succeeded!
```

Press `Ctrl+C` to exit.

✅ **If connection succeeds, AGI is OK!**

### Test 5: Network Connectivity

```bash
# Check if ports are listening
netstat -an | findstr "5060"
netstat -an | findstr "8000"
netstat -an | findstr "3000"
```

**Expected output:**
```
TCP    0.0.0.0:5060           0.0.0.0:0              LISTENING
UDP    0.0.0.0:5060           :*
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING
```

✅ **If all ports are listening, Network is OK!**

---

## Phase 3: SIP Client Testing (PC)

### Step 1: Install MicroSIP

1. Download: https://www.microsip.org/downloads
2. Install and open MicroSIP

### Step 2: Configure MicroSIP

1. Click **"Add Account"** → **Manual Configuration**
2. Enter:
   - **Account Name:** Test PC
   - **SIP Server:** localhost
   - **Port:** 5060
   - **Username:** 6002
   - **Password:** 6002
   - **Transport:** UDP
3. Save and close settings

### Step 3: Register

1. In MicroSIP main window:
   - Status should show **green (Registered)**
   - If red, click to see error message

2. Verify registration in Asterisk:
```bash
docker exec asterisk asterisk -rx "pjsip show endpoints"
```

**Expected output:**
```
Endpoint:  6002/6002                                             Avail         1 of 10
```

✅ **If registered, SIP Registration is OK!**

### Step 4: Test Echo Call (Extension 200)

1. In MicroSIP:
   - Click dialpad
   - Dial: **200**
   - Click green call button
   - **Expected:** Hear "The echo test has started..."
   - Speak into microphone
   - **Expected:** Hear your voice echoed back
   - Hang up

2. Monitor in Asterisk CLI:
```bash
docker exec -it asterisk asterisk -rvvvv
```

**Expected output:**
```
-- Executing [200@from-internal:1] NoOp("PJSIP/6002-00000001", "=== Echo Test ===")
-- Executing [200@from-internal:2] Answer("PJSIP/6002-00000001", "")
-- Executing [200@from-internal:3] Playback("PJSIP/6002-00000001", "demo-echotest")
-- Executing [200@from-internal:4] Echo("PJSIP/6002-00000001", "")
```

✅ **If echo works, Basic Calling is OK!**

### Step 5: Test AI Agent (Extension 100)

1. In MicroSIP:
   - Dial: **100**
   - Click call
   - **Expected:** After 2-3 seconds, hear AI greeting
   - Try saying: **"I want to check my bill"**
   - **Expected:** AI asks for customer ID
   - Say: **"1"** (first customer in database)
   - **Expected:** AI provides billing information

2. Monitor backend logs:
```bash
docker logs backend -f
```

**Expected output:**
```
INFO: New call from Unknown
INFO: User said: I want to check my bill
INFO: Detected intent: billing
INFO: AI responds: I'd be happy to help you with your billing inquiry...
```

✅ **If AI responds, AI Agent is OK!**

---

## Phase 4: iPhone Testing

### Step 1: Verify PC Network

```bash
# Get your PC's IP
ipconfig | findstr "IPv4"
```

Should show: `192.168.1.19` (or similar)

### Step 2: Test from iPhone Safari

1. On iPhone, open Safari
2. Go to: `http://192.168.1.19:8000/health`
3. **Expected:** See `{"status":"healthy","version":"1.0.0"}`

✅ **If this works, iPhone can reach PC!**

### Step 3: Install Zoiper on iPhone

1. Open App Store
2. Search **"Zoiper Lite"**
3. Install

### Step 4: Configure Zoiper

1. Open Zoiper → **Settings** → **Accounts** → **Add Account** → **Manual**
2. Enter:
   - **Account Type:** SIP
   - **Domain:** `192.168.1.19` (your PC IP)
   - **Username:** 6001
   - **Password:** 6001
   - **Port:** 5060
   - **Transport:** UDP
3. **Advanced Settings:**
   - **STUN Server:** `stun.l.google.com:19302`
   - **Enable STUN:** ON
4. **Codecs:**
   - Enable: PCMU, PCMA, GSM
   - Disable: All video codecs
5. Save

### Step 5: Register iPhone

1. In Zoiper:
   - Status should show **"Registered"** (green)

2. Verify in Asterisk:
```bash
docker exec asterisk asterisk -rx "pjsip show endpoints"
```

**Expected:**
```
Endpoint:  6001/6001                                             Avail         1 of 10
Endpoint:  6002/6002                                             Avail         1 of 10
```

✅ **If both registered, Multi-Device is OK!**

### Step 6: Test Call from iPhone

1. **Dial 200** for echo test:
   - Should hear echo announcement
   - Speak and hear echo back

2. **Dial 100** for AI agent:
   - Should hear AI greeting
   - Try conversation

✅ **If both work, iPhone Calling is OK!**

---

## Phase 5: Monitoring & Verification

### Monitor Active Calls

**Terminal 1 - Asterisk CLI:**
```bash
docker exec -it asterisk asterisk -rvvvv
```

**Terminal 2 - Backend Logs:**
```bash
docker logs backend -f
```

**Terminal 3 - Container Stats:**
```bash
docker stats
```

### View Call in Dashboard

1. Open browser: `http://localhost:3000`
2. Click **"Calls"** tab
3. See your test calls listed
4. Click **"View Details"** to see transcript

---

## ✅ Success Checklist

After running all tests, verify:

- [ ] All containers running (`docker-compose ps`)
- [ ] Backend API responding (`curl http://localhost:8000/health`)
- [ ] Dashboard accessible (`http://localhost:3000`)
- [ ] Asterisk endpoints showing (`pjsip show endpoints`)
- [ ] AGI connection working (`nc -v backend 4573`)
- [ ] MicroSIP registered on PC
- [ ] Echo test (200) working from PC
- [ ] AI agent (100) working from PC
- [ ] iPhone can access PC (`http://192.168.1.19:8000/health`)
- [ ] Zoiper registered on iPhone
- [ ] Calls working from iPhone

---

## 🆘 Troubleshooting

### If Something Fails

1. **Note the failure point:**
   - Phase number (1-5)
   - Step number
   - Error message

2. **Collect logs:**
```bash
docker-compose logs > alllogs.txt
```

3. **Check specific service:**
```bash
# Backend logs
docker logs backend

# Asterisk logs
docker logs asterisk

# Dashboard logs
docker logs dashboard
```

4. **Common issues:**

   **Port already in use:**
   ```bash
   # Find process using port
   netstat -ano | findstr ":5060"
   # Kill process (replace PID)
   taskkill /PID <PID> /F
   ```

   **Container won't start:**
   ```bash
   # Check container logs
   docker logs <container-name>
   # Restart specific container
   docker-compose restart <service-name>
   ```

   **SIP registration fails:**
   - Check firewall settings
   - Verify IP address is correct
   - Check Asterisk logs: `docker logs asterisk`
   - Verify endpoints: `docker exec asterisk asterisk -rx "pjsip show endpoints"`

   **AI agent not responding:**
   - Check backend logs: `docker logs backend -f`
   - Verify AGI connection: `docker exec asterisk nc -v backend 4573`
   - Check database: `docker exec backend python -m db.init_db`

---

## Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart <service-name>

# Check status
docker-compose ps

# Access Asterisk CLI
docker exec -it asterisk asterisk -rvvvv

# Check SIP endpoints
docker exec asterisk asterisk -rx "pjsip show endpoints"

# Test backend API
curl http://localhost:8000/health

# Initialize database
docker exec backend python -m db.init_db
```

---

## Support

If you encounter issues not covered in this guide:

1. Check the logs: `docker-compose logs > alllogs.txt`
2. Review the error messages
3. Verify all configuration files are correct
4. Ensure all required ports are available
5. Check network connectivity between devices

Good luck with your testing! 🚀

