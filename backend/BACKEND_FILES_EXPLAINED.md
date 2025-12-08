# Backend Python Files Explained

This document explains what each Python file in the `backend/` folder does.

---

## 📁 Root Level Files

### `main.py`
**Purpose**: Main entry point for the entire backend system  
**What it does**:
- Starts two servers concurrently:
  1. **AGI Server** (port 4573) - Handles communication with Asterisk PBX for phone calls
  2. **FastAPI Server** (port 8000) - Provides REST API endpoints for the dashboard
- Configures logging
- Orchestrates the entire backend startup process

**When to use**: Run this to start the full backend system (`python main.py`)

---

### `config.py`
**Purpose**: Central configuration file  
**What it does**:
- Loads environment variables from `.env` file
- Defines all system settings:
  - Database connection (SQLite)
  - API host/port
  - Asterisk connection settings
  - AI model configuration (Ollama)
  - ASR/TTS engine settings
  - Company information
  - Feature flags
- Creates necessary directories (data, logs, recordings, knowledge)

**When to use**: Imported by other files to access configuration values

---

## 🧪 Testing/Interface Files

### `web_test.py`
**Purpose**: Simple web-based chat interface for testing the AI agent  
**What it does**:
- Creates a FastAPI server on port 8001
- Provides a beautiful HTML chat interface
- Uses WebSockets for real-time communication
- Allows text-based testing of the AI agent without voice

**When to use**: Quick testing of AI agent logic without voice complexity  
**Access**: `http://localhost:8001`

---

### `voicetest.py`
**Purpose**: Basic WebRTC voice interface for testing  
**What it does**:
- Creates a FastAPI server on port 8003
- Uses browser's Web Speech API for speech recognition
- Uses browser's Speech Synthesis API for text-to-speech
- Provides a simple voice conversation interface
- Mobile-friendly (works on iPhone Safari)

**When to use**: Testing voice interaction on mobile devices  
**Access**: `http://localhost:8003` (or your IP:8003 on mobile)

---

### `voiceproduction.py`
**Purpose**: Production-ready voice interface with advanced features  
**What it does**:
- Creates a FastAPI server on port 8004
- Enhanced features:
  - Microphone level monitoring
  - Varied greetings and farewells
  - Better error handling
  - Database call recording (saves transcripts, duration, intent)
  - Improved silence detection
  - Confidence filtering for speech recognition
- Tracks active calls in memory
- Updates call records in database

**When to use**: Production deployment or advanced testing  
**Access**: `http://localhost:8004`

---

### `voicemobile.py`
**Purpose**: Mobile-optimized voice interface (best for iPhone)  
**What it does**:
- Creates a FastAPI server on port 8004
- Optimized specifically for mobile devices:
  - Enhanced speech recognition settings (`continuous=true`, `interimResults=true`)
  - Explicit microphone permission handling
  - Better error messages for mobile users
  - Detailed console logging for debugging
  - Handles iOS-specific quirks
- Automatically restarts recognition after AI speaks
- Properly stops microphone when call ends

**When to use**: Testing on iPhone or other mobile devices  
**Access**: `http://YOUR_IP:8004` on mobile Safari

---

### `voiceptt.py`
**Purpose**: Push-to-Talk voice interface (alternative to continuous listening)  
**What it does**:
- Creates a FastAPI server on port 8005
- User holds a button to speak (like walkie-talkie)
- More reliable than continuous speech recognition
- Better for noisy environments or unreliable microphones

**When to use**: If continuous speech recognition is unreliable  
**Access**: `http://localhost:8005`

---

### `simplevoicetest.py`
**Purpose**: Minimal test server to verify speech synthesis works  
**What it does**:
- Very simple FastAPI server on port 8005
- Just tests if browser speech synthesis works
- No AI agent, no WebSockets, just a test button

**When to use**: Quick check if browser TTS is working  
**Access**: `http://localhost:8005`

---

## 🤖 Agent Module (`agent/`)

### `agent/agent.py`
**Purpose**: Core AI agent logic - the "brain" of the system  
**What it does**:
- Processes user input and generates intelligent responses
- Manages conversation state (customer ID, intent, retry count)
- Routes requests to appropriate handlers based on intent:
  - **Billing**: Handles bill inquiries, balance checks
  - **Technical Support**: Creates support tickets
  - **Account Info**: Provides account details
  - **New Service**: Routes to sales
- Extracts customer IDs from user input
- Verifies customer IDs against database
- Handles errors gracefully with retry logic
- Can use LLM (Ollama) or rule-based responses
- Creates support tickets when needed

**Key Methods**:
- `process_input()` - Main method that processes user input
- `handle_billing()` - Handles billing-related queries
- `handle_account_info()` - Provides account information
- `get_customer()` - Retrieves customer from database
- `extract_customer_id()` - Finds customer ID in user text

**When to use**: This is the core logic - imported by all voice/web interfaces

---

### `agent/intent_classifier.py`
**Purpose**: Classifies user intent from their text  
**What it does**:
- Analyzes user input to determine what they want:
  - `greeting` - Hello, hi, etc.
  - `billing` - Bill, payment, charge, invoice
  - `technical_support` - Not working, broken, slow, issue
  - `account_info` - Account, information, details
  - `new_service` - New, activate, sign up
  - `cancellation` - Cancel, terminate
  - `complaint` - Complain, unhappy, frustrated
- Uses keyword matching with scoring
- Returns the highest-scoring intent

**When to use**: Used by `agent.py` to route requests correctly

---

### `agent/knowledge_base.py`
**Purpose**: Stores company-specific knowledge and responses  
**What it does**:
- Loads knowledge from `knowledge/company_kb.json`
- Provides default responses for common questions
- Stores FAQ entries
- Provides context for LLM responses
- Can add/update FAQ entries dynamically

**When to use**: Used by `agent.py` for general queries and LLM context

---

## 🌐 API Module (`api/`)

### `api/server.py`
**Purpose**: Main FastAPI application setup  
**What it does**:
- Creates the FastAPI app instance
- Configures CORS (Cross-Origin Resource Sharing)
- Includes all API routes from `routes.py`
- Provides root and health check endpoints
- Sets up startup/shutdown events

**When to use**: Imported by `main.py` to start the API server

---

### `api/routes.py`
**Purpose**: Defines all REST API endpoints  
**What it does**:
- **Customer Endpoints**:
  - `GET /api/customers` - List all customers
  - `GET /api/customers/{id}` - Get customer by ID
  - `POST /api/customers` - Create new customer

- **Call Endpoints**:
  - `GET /api/calls` - List all calls
  - `GET /api/calls/recent` - Get recent calls with details
  - `GET /api/calls/live` - Get currently active calls
  - `GET /api/calls/{id}/transcript` - Get formatted transcript
  - `GET /api/calls/customer/{id}` - Get calls for a customer

- **Ticket Endpoints**:
  - `GET /api/tickets` - List all tickets
  - `POST /api/tickets` - Create ticket
  - `PATCH /api/tickets/{id}` - Update ticket

- **Analytics Endpoints**:
  - `GET /api/analytics` - Get analytics summary
  - `GET /api/analytics/daily` - Get daily analytics
  - `GET /api/analytics/intents` - Get intent distribution

**When to use**: Used by the dashboard to fetch data

---

## 💾 Database Module (`db/`)

### `db/database.py`
**Purpose**: Database connection and session management  
**What it does**:
- Creates SQLAlchemy engine (connects to SQLite database)
- Creates session factory for database sessions
- Provides `get_db()` function for dependency injection
- Defines `Base` class for all database models

**When to use**: Imported by models and other files that need database access

---

### `db/models.py`
**Purpose**: Defines database table structures  
**What it does**:
- **Customer Model**: Stores customer information (name, phone, email, plan, balance, status)
- **Call Model**: Stores call records (caller, duration, transcript, intent, status)
- **Ticket Model**: Stores support tickets (type, description, status, priority)
- **Analytics Model**: Stores analytics data (call counts, averages, etc.)
- Defines relationships between tables (Customer → Calls, Customer → Tickets)

**When to use**: Used by SQLAlchemy to create tables and query data

---

### `db/init_db.py`
**Purpose**: Initializes database with tables and sample data  
**What it does**:
- Creates all database tables if they don't exist
- Seeds database with sample customers, calls, tickets, and analytics
- Only runs if database is empty (won't overwrite existing data)

**When to use**: Run once to set up the database: `python -m db.init_db`

---

## 📞 AGI Module (`agi/`)

### `agi/agi_handler.py`
**Purpose**: Handles communication with Asterisk PBX for phone calls  
**What it does**:
- Starts an AGI (Asterisk Gateway Interface) server on port 4573
- Listens for incoming calls from Asterisk
- Reads AGI environment variables (caller ID, etc.)
- Records audio from the call
- Transcribes audio using Whisper ASR
- Gets AI response from agent
- Converts response to speech using TTS
- Plays audio back to caller
- Saves call transcript to database

**When to use**: Used by `main.py` to handle phone calls via Asterisk

---

## 🎤 ASR Module (`asr/`)

### `asr/whisper_engine.py`
**Purpose**: Speech-to-Text engine using OpenAI Whisper  
**What it does**:
- Loads Whisper model (configurable: tiny, base, small, medium, large)
- Transcribes audio data (numpy arrays) to text
- Transcribes audio files to text
- Detects language from audio
- Handles errors gracefully

**When to use**: Used by `agi_handler.py` to transcribe phone call audio

---

## 🔊 TTS Module (`tts/`)

### `tts/tts_engine.py`
**Purpose**: Text-to-Speech engine using Piper (fallback to espeak)  
**What it does**:
- Synthesizes text to speech audio
- Saves audio to files
- Caches generated audio to avoid regenerating
- Uses espeak as fallback if Piper not available
- Creates silent audio as last resort fallback

**When to use**: Used by `agi_handler.py` to convert AI responses to speech for phone calls

---

### `tts/edgetts_engine.py`
**Purpose**: Human-like TTS using Microsoft Edge-TTS (FREE)  
**What it does**:
- Uses Edge-TTS API for natural-sounding speech
- Supports multiple voices (male/female variants)
- Caches audio files
- Provides async and sync interfaces
- Much better quality than browser TTS

**When to use**: Can be used instead of browser TTS for better quality (not currently integrated in voice interfaces)

---

## 📝 Summary

**Core System Files**:
- `main.py` - Starts everything
- `config.py` - Configuration
- `agent/agent.py` - AI logic
- `api/server.py` + `api/routes.py` - REST API
- `db/*` - Database models and setup

**Voice Interfaces** (choose one):
- `voicetest.py` - Basic voice testing
- `voiceproduction.py` - Production-ready
- `voicemobile.py` - Best for iPhone
- `voiceptt.py` - Push-to-talk alternative

**Supporting Modules**:
- `agi/` - Phone call handling
- `asr/` - Speech recognition
- `tts/` - Text-to-speech
- `agent/` - AI intelligence

---

## 🚀 Quick Start Guide

1. **Start full system**: `python main.py` (starts AGI + API servers)
2. **Test web chat**: `python web_test.py` → `http://localhost:8001`
3. **Test voice (mobile)**: `python voicemobile.py` → `http://YOUR_IP:8004`
4. **Initialize database**: `python -m db.init_db`

---

## 🔍 File Dependencies

```
main.py
├── api/server.py
│   └── api/routes.py
│       └── db/models.py
├── agi/agi_handler.py
│   ├── agent/agent.py
│   │   ├── agent/intent_classifier.py
│   │   └── agent/knowledge_base.py
│   ├── asr/whisper_engine.py
│   └── tts/tts_engine.py
└── config.py
    └── db/database.py
        └── db/models.py
```

All voice interfaces (`voicetest.py`, `voiceproduction.py`, etc.) import `agent/agent.py` directly.

