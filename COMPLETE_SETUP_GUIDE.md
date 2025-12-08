# 🚀 Complete Setup & Testing Guide

This guide will help you get everything working from scratch.

---

## ✅ What You'll Get

- **Natural Human-Like Voice** (Edge-TTS - Microsoft Neural Voices)
- **Smart AI Agent** (Ollama-powered, understands context)
- **Working Database** (Sample customers ready to test)
- **Voice Interface** (Production-ready at port 8004)

---

## 📋 Step 1: Initialize Database

**This is CRITICAL - Do this first!**

```bash
# Initialize database with sample customers
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
Database initialization complete!
```

**If you see "Database already contains data":**
- That's OK! The database is already set up.
- You can still use it with sample customers (IDs: 1, 2, 3, 4, 5)

---

## 📋 Step 2: Install Edge-TTS (Natural Voice)

```bash
# Install Edge-TTS for human-like voice
docker exec backend pip install edge-tts
```

**Expected Output:**
```
Successfully installed edge-tts-7.2.3 tabulate-0.9.0
```

---

## 📋 Step 3: Start Voice Interface

```bash
# Start the production voice interface
docker exec -d backend python voiceproduction.py
```

**Verify it's running:**
```bash
docker exec backend ps aux | findstr voiceproduction
```

You should see a Python process running.

---

## 📋 Step 4: Test Everything

### Open Voice Interface:
1. **Open browser**: `http://localhost:8004`
2. **Click "Start Call"**
3. **Allow microphone access**
4. **Wait for AI greeting** (should sound natural, not robotic!)

### Test Billing (This Should Work Now!):

**Conversation:**
```
You: "Hi, I want to check my billing information"
AI: "I'd be happy to help with your billing. Can you please provide your customer ID for verification?"
You: "My ID is 1"
AI: "Thanks, John Doe. I found your account. Your current balance is $99.99 and your plan is Premium. Would you like to make a payment or have any other questions?"
```

**The AI should:**
- ✅ Actually ask for customer ID (not just say "sure")
- ✅ Actually provide billing information when ID is given
- ✅ Sound natural (not robotic)

---

## 🎤 TTS (Text-to-Speech) - What We're Using

### **Edge-TTS** (Microsoft Neural Voices)
- **What it is**: Free Microsoft Edge TTS API
- **Why we use it**: Sounds very natural and human-like
- **Voice**: `en-US-AriaNeural` (friendly female voice)
- **Reliability**: Works everywhere, no API keys needed
- **Fallback**: If Edge-TTS fails, falls back to browser TTS

### How It Works:
1. AI generates text response
2. Backend sends text to Edge-TTS
3. Edge-TTS generates MP3 audio file
4. Browser plays the audio
5. Sounds natural and human-like!

---

## 🔧 Troubleshooting

### Issue: "Agent says 'sure' but does nothing"

**Fixed!** The agent now:
- ✅ Actually asks for customer ID
- ✅ Actually provides billing info when ID is given
- ✅ Uses structured logic first, then enhances with Ollama

**If still having issues:**
```bash
# Restart the voice service
docker exec backend pkill -f voiceproduction.py
docker exec -d backend python voiceproduction.py
```

### Issue: "Voice sounds robotic"

**Check Edge-TTS is installed:**
```bash
docker exec backend pip show edge-tts
```

**If not installed:**
```bash
docker exec backend pip install edge-tts
docker exec backend pkill -f voiceproduction.py
docker exec -d backend python voiceproduction.py
```

**Check browser console (F12)** - you should see:
```
🔊 Generating natural speech for: ...
✅ Audio loaded, playing...
```

### Issue: "Database not working"

**Reinitialize:**
```bash
# Remove old database
docker exec backend rm -f data/callcenter.db

# Reinitialize
docker exec backend python -m db.init_db
```

### Issue: "Can't access from mobile"

**Find your IP:**
- Windows: `ipconfig` (look for IPv4 Address)
- Mac/Linux: `ifconfig`

**On mobile, use:** `http://YOUR_IP:8004`
- Make sure same WiFi network
- Use Safari (not Chrome) on iPhone

---

## 📊 Sample Customers (For Testing)

After database initialization, you have:

| ID | Name | Balance | Plan | Status |
|----|------|---------|------|--------|
| 1 | John Doe | $99.99 | Premium | active |
| 2 | Jane Smith | $49.99 | Standard | active |
| 3 | Bob Johnson | $29.99 | Basic | active |
| 4 | Alice Williams | $0.00 | Premium | suspended |
| 5 | Charlie Brown | $49.99 | Standard | active |

**Use these IDs to test!**

---

## 🧪 Complete Test Scenarios

### Test 1: Billing Inquiry
```
1. Say: "I want to check my bill"
2. AI asks for ID
3. Say: "My ID is 1"
4. AI provides: "Thanks, John Doe. Your balance is $99.99..."
```

### Test 2: Account Information
```
1. Say: "Can you tell me about my account?"
2. AI asks for ID
3. Say: "It's 2"
4. AI provides account details
```

### Test 3: Technical Support
```
1. Say: "My internet is slow"
2. AI asks for ID
3. Say: "ID is 3"
4. AI creates ticket and confirms
```

---

## ✅ Verification Checklist

Before testing, verify:

- [ ] Database initialized: `docker exec backend python -m db.init_db`
- [ ] Edge-TTS installed: `docker exec backend pip show edge-tts`
- [ ] Voice service running: `docker exec backend ps aux | findstr voiceproduction`
- [ ] Can access: `http://localhost:8004`
- [ ] Microphone permission granted
- [ ] Browser console shows TTS generation (F12)

---

## 🎯 Quick Commands Reference

```bash
# Initialize database
docker exec backend python -m db.init_db

# Install Edge-TTS
docker exec backend pip install edge-tts

# Start voice interface
docker exec -d backend python voiceproduction.py

# Check if running
docker exec backend ps aux | findstr voiceproduction

# Restart voice interface
docker exec backend pkill -f voiceproduction.py
docker exec -d backend python voiceproduction.py

# Check database
docker exec backend python -c "from db.database import SessionLocal; from db.models import Customer; db = SessionLocal(); print(f'Customers: {db.query(Customer).count()}'); db.close()"
```

---

## 🎉 You're Ready!

1. **Database**: ✅ Initialized with sample customers
2. **TTS**: ✅ Edge-TTS installed (natural voice)
3. **Agent**: ✅ Fixed to actually work (not just say "sure")
4. **Voice Interface**: ✅ Running at `http://localhost:8004`

**Open `http://localhost:8004` and test it!**

The agent should now:
- ✅ Actually ask for customer ID when you say "check my billing"
- ✅ Actually provide billing information when you give an ID
- ✅ Sound natural and human-like (not robotic)

---

## 📞 Need Help?

**Check logs:**
```bash
# Backend logs
docker-compose logs backend

# Voice service logs (if running in foreground)
docker exec backend python voiceproduction.py
```

**Common Issues:**
- See `DATABASE_SETUP.md` for database issues
- See `STARTUP_GUIDE.md` for general setup
- Check browser console (F12) for frontend errors

---

**Enjoy your AI Call Center!** 🚀

