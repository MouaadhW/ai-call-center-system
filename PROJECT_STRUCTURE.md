# AI Call Center System

## 🎉 Project Complete!

This is a fully functional, self-hosted AI-powered call center system.

### 📁 Project Structure

```
ai-call-center-system/
├── README.md                    # Project overview
├── INSTALLATION.md              # Detailed setup guide
├── QUICKSTART.md                # 5-minute quick start
├── TESTING.md                   # Testing procedures
├── docker-compose.yml           # Docker orchestration
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── docker/
│   └── asterisk/                # Asterisk PBX configuration
│       ├── Dockerfile
│       ├── asterisk.conf
│       ├── modules.conf
│       ├── pjsip.conf
│       └── extensions.conf
│
├── backend/                     # Python backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.py
│   ├── main.py
│   ├── agi/                     # AGI call handler
│   ├── asr/                     # Speech recognition
│   ├── tts/                     # Text-to-speech
│   ├── agent/                   # AI agent
│   ├── db/                      # Database models
│   ├── api/                     # REST API
│   └── knowledge/               # Knowledge base
│
├── dashboard/                   # React dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── components/
│       │   ├── Dashboard.js
│       │   ├── CallList.js
│       │   ├── Analytics.js
│       │   └── Settings.js
│       └── services/
│           └── api.js
│
└── scripts/                     # Utility scripts
    ├── setup.sh
    └── test_call.py
```

### 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd ai-call-center-system
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Initialize database
docker exec -it backend python -m db.init_db

# 4. Access dashboard
open http://localhost:3000
```

### 🔧 System Components

- **Asterisk PBX** (port 5060) - VoIP call handling
- **Backend API** (port 8000) - FastAPI server
- **Dashboard** (port 3000) - React web interface
- **AGI Server** (port 4573) - Call processing

### 📞 Test the System

1. Install a SIP softphone (Zoiper, Linphone)
2. Configure: `localhost:5060`, user: `6001`, pass: `6001`
3. Call extension `100` to talk to the AI agent

### 📊 Features

✅ Automatic call answering
✅ Speech-to-text (Whisper)
✅ AI conversation (LLM)
✅ Text-to-speech (Piper)
✅ Intent classification
✅ Customer verification
✅ Ticket creation
✅ Real-time analytics
✅ Call transcripts

### 🛠️ Tech Stack

- **VoIP**: Asterisk 20
- **Backend**: Python 3.11, FastAPI
- **AI**: Whisper, Piper TTS, Ollama/OpenAI
- **Database**: SQLite
- **Frontend**: React 18, Recharts
- **Container**: Docker

### 📚 Documentation

- [README.md](README.md) - Overview
- [INSTALLATION.md](INSTALLATION.md) - Setup guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [TESTING.md](TESTING.md) - Testing guide

### 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

### 📄 License

MIT License

### 👨‍💻 Author

Mouaadh W - @MouaadhW

---

**Need help?** Check the documentation or open an issue.
