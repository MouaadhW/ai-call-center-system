# 🚀 Complete Startup Guide - AI Call Center System

This guide will help you start and test the entire AI Call Center system.

---

## 📋 Prerequisites

1. **Docker & Docker Compose** - Installed and running
2. **Ollama** - For AI agent intelligence (optional but recommended)
3. **Browser** - Chrome, Edge, or Safari (for voice interface)
4. **Microphone** - For voice testing

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Make sure you're in the project root
cd ai-call-center-system

# Install Python dependencies in Docker container
docker exec backend pip install edge-tts
```

### Step 2: Start All Services

```bash
# Start all Docker services (Asterisk, Backend, Dashboard)
docker-compose up -d

# Wait 10-15 seconds for services to start
```

### Step 3: Initialize Database

```bash
# Initialize database with sample data
docker exec backend python -m db.init_db
```

### Step 4: Start Voice Interface

```bash
# Start the production voice interface
docker exec -d backend python voiceproduction.py
```

### Step 5: Test It!

1. **Open your browser**: `http://localhost:8004`
2. **Click "Start Call"**
3. **Allow microphone access**
4. **Start talking!**

---

## 🔧 Detailed Setup

### 1. Check Docker Services Status

```bash
# Check if all services are running
docker-compose ps

# You should see:
# - asterisk (running)
# - backend (running)
# - dashboard (running)
```

### 2. Verify Backend API

```bash
# Test backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy","version":"1.0.0"}
```

### 3. Check Voice Service

```bash
# Check if voiceproduction.py is running
docker exec backend ps aux | findstr voiceproduction

# Should show a Python process running voiceproduction.py
```

### 4. Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Voice Interface** | `http://localhost:8004` | Main voice conversation interface |
| **Web Chat Test** | `http://localhost:8001` | Text-based chat testing |
| **Dashboard** | `http://localhost:3000` | Call center dashboard |
| **Backend API** | `http://localhost:8000` | REST API endpoints |

---

## 🧪 Testing the System

### Test 1: Voice Conversation (Recommended)

1. Open `http://localhost:8004` in your browser
2. Click **"Start Call"**
3. Allow microphone access when prompted
4. Wait for AI greeting
5. Try these conversations:

**Billing Inquiry:**
- You: "Hi, I want to check my bill"
- AI: (asks for customer ID)
- You: "My ID is 1"
- AI: (provides billing information naturally)

**Technical Support:**
- You: "My internet is really slow"
- AI: (asks for customer ID, then creates ticket)

**Account Information:**
- You: "Can you tell me about my account?"
- AI: (asks for ID, then provides account details)

### Test 2: Web Chat Interface

1. Open `http://localhost:8001` in your browser
2. Type your message
3. See AI responses in real-time
4. Test the same conversations as above

### Test 3: Dashboard

1. Open `http://localhost:3000`
2. View:
   - Recent calls
   - Analytics
   - Customer information
   - Support tickets

---

## 🎤 Voice Features

### Natural Human-Like Voice
- Uses **Edge-TTS** (Microsoft Neural Voices)
- Sounds natural and conversational
- No robotic voice!

### Smart AI Agent
- Uses **Ollama** for intelligent responses
- Understands context and conversation flow
- Remembers what you said earlier

### Microphone Detection
- Real-time audio level monitoring
- Continuous speech recognition
- Better voice pickup

---

## 🔍 Troubleshooting

### Issue: "Microphone not working"

**Solution:**
1. Check browser permissions (click lock icon in address bar)
2. Make sure microphone is not muted
3. Try refreshing the page
4. Check browser console (F12) for errors

### Issue: "Voice sounds robotic"

**Solution:**
1. Make sure Edge-TTS is installed: `docker exec backend pip install edge-tts`
2. Restart voice service: 
   ```bash
   docker exec backend pkill -f voiceproduction.py
   docker exec -d backend python voiceproduction.py
   ```
3. Clear browser cache and refresh

### Issue: "AI responses are not smart"

**Solution:**
1. Check if Ollama is running: `docker exec backend python -c "import ollama; print('OK')"`
2. Verify Ollama model: Check `config.py` for `LLM_MODEL` setting
3. Default model: `llama3.2:3b` (should be downloaded automatically)

### Issue: "Can't access from mobile/iPhone"

**Solution:**
1. Find your computer's IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Mac/Linux: `ifconfig` or `ip addr`
2. On iPhone, use: `http://YOUR_IP:8004`
3. Make sure iPhone and computer are on same WiFi network
4. Use Safari (not Chrome) on iPhone

### Issue: "Services not starting"

**Solution:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs asterisk

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up -d --build
```

---

## 📱 Mobile Testing (iPhone/Android)

### On iPhone:

1. **Find your computer's IP** (e.g., `192.168.1.19`)
2. **Open Safari** (not Chrome)
3. **Go to**: `http://YOUR_IP:8004`
4. **Tap "Start Call"**
5. **Allow microphone** when prompted
6. **Speak clearly** after AI greeting

### Tips for Mobile:
- Use Safari (best compatibility)
- Speak clearly and wait for "Listening..." status
- Say "goodbye" to end call
- Check microphone permissions in Safari settings

---

## 🎯 Complete Startup Script

Create a file `start_all.bat` (Windows) or `start_all.sh` (Mac/Linux):

### Windows (`start_all.bat`):
```batch
@echo off
echo Starting AI Call Center System...
echo.

echo [1/5] Starting Docker services...
docker-compose up -d

echo [2/5] Waiting for services to start...
timeout /t 10

echo [3/5] Installing Edge-TTS...
docker exec backend pip install -q edge-tts

echo [4/5] Initializing database...
docker exec backend python -m db.init_db

echo [5/5] Starting voice interface...
docker exec -d backend python voiceproduction.py

echo.
echo ========================================
echo ✅ System Started Successfully!
echo ========================================
echo.
echo 📱 Voice Interface: http://localhost:8004
echo 💬 Web Chat: http://localhost:8001
echo 📊 Dashboard: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
```

### Mac/Linux (`start_all.sh`):
```bash
#!/bin/bash
echo "Starting AI Call Center System..."
echo

echo "[1/5] Starting Docker services..."
docker-compose up -d

echo "[2/5] Waiting for services to start..."
sleep 10

echo "[3/5] Installing Edge-TTS..."
docker exec backend pip install -q edge-tts

echo "[4/5] Initializing database..."
docker exec backend python -m db.init_db

echo "[5/5] Starting voice interface..."
docker exec -d backend python voiceproduction.py

echo
echo "========================================"
echo "✅ System Started Successfully!"
echo "========================================"
echo
echo "📱 Voice Interface: http://localhost:8004"
echo "💬 Web Chat: http://localhost:8001"
echo "📊 Dashboard: http://localhost:3000"
echo
```

Make it executable:
```bash
chmod +x start_all.sh
```

---

## 🛑 Stopping the System

```bash
# Stop voice interface
docker exec backend pkill -f voiceproduction.py

# Stop all services
docker-compose down

# Or stop and remove volumes (clean reset)
docker-compose down -v
```

---

## 📊 System Architecture

```
┌─────────────┐
│   Browser   │ (Voice Interface)
│  localhost  │
│    :8004    │
└──────┬──────┘
       │ WebSocket
       ▼
┌─────────────┐
│   Backend   │ (FastAPI + Ollama)
│  localhost  │
│    :8000    │
└──────┬──────┘
       │
       ├──► Database (SQLite)
       ├──► Ollama (AI)
       └──► Edge-TTS (Voice)
```

---

## ✅ Verification Checklist

- [ ] Docker services running (`docker-compose ps`)
- [ ] Backend API responding (`curl http://localhost:8000/health`)
- [ ] Database initialized (`docker exec backend python -m db.init_db`)
- [ ] Voice service running (`docker exec backend ps aux | findstr voiceproduction`)
- [ ] Edge-TTS installed (`docker exec backend pip show edge-tts`)
- [ ] Ollama available (`docker exec backend python -c "import ollama"`)
- [ ] Can access `http://localhost:8004`
- [ ] Microphone permission granted
- [ ] Voice sounds natural (not robotic)
- [ ] AI responses are intelligent and contextual

---

## 🎉 You're Ready!

Once all checks pass, you can:
1. **Test voice conversations** at `http://localhost:8004`
2. **View analytics** at `http://localhost:3000`
3. **Test text chat** at `http://localhost:8001`

**Enjoy your AI Call Center!** 🚀

---

## 📞 Sample Conversations

### Billing:
```
You: "Hi, I'd like to check my bill"
AI: "I'd be happy to help with your billing. Can you please provide your customer ID for verification?"
You: "It's 1"
AI: "Thanks, John Doe. I found your account. Your current balance is $99.99 and your plan is Premium. Would you like to make a payment or have any other questions?"
```

### Technical Support:
```
You: "My internet is really slow today"
AI: "I'll help you with that technical issue. First, can you provide your customer ID?"
You: "My ID is 2"
AI: "Thanks, Jane Smith. I found your account. Can you please describe the technical issue you're experiencing?"
You: "The connection keeps dropping"
AI: "I've created a support ticket #1 for you, Jane Smith. Our technical team will contact you within 24 hours. Is there anything else I can help you with?"
```

---

## 🔗 Quick Links

- **Voice Interface**: http://localhost:8004
- **Web Chat**: http://localhost:8001  
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

**Need Help?** Check the logs:
```bash
docker-compose logs backend
docker exec backend tail -f logs/callcenter.log
```

