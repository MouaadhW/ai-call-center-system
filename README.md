# 🤖 AI Call Center System

A fully self-hosted, low-cost AI-powered call center system that automatically handles customer calls using:

- **Asterisk PBX** for VoIP call handling
- **Whisper ASR** for speech-to-text
- **Local LLM** for intelligent conversation
- **Piper TTS** for text-to-speech
- **FastAPI** backend
- **React** dashboard

## 🎯 Features

✅ Automatic call answering and routing  
✅ Intent detection and classification  
✅ Customer verification  
✅ Knowledge base integration  
✅ Ticket creation and management  
✅ Real-time analytics dashboard  
✅ Call transcripts and recordings  
✅ Multi-language support  
✅ Fully offline capable

## 🏗️ Architecture

```
Incoming Call → Asterisk PBX → AGI Handler → AI Agent
                                     ↓
                           ASR ← → TTS
                                     ↓
                        Knowledge Base + DB
                                     ↓
                        Analytics Dashboard
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum
- Python 3.9+
- Node.js 16+ (for dashboard)

### Installation

1. **Clone the repository**
```bash
git clone /ai-call-center-system.git
cd ai-call-center-system
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
docker exec -it backend python -m db.init_db
```

5. **Access dashboard**
```
http://localhost:3000
```

## 📖 Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- Quick Start Guide - Get running in 5 minutes
- Testing Guide - How to test with softphone

## 🔧 Configuration

### Asterisk SIP Configuration

Edit `docker/asterisk/pjsip.conf` to add SIP endpoints:

```ini
[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001
aors=6001
```

### Knowledge Base

Edit `backend/knowledge/company_kb.json` to customize responses:

```json
{
  "intents": {
    "billing": {
      "keywords": ["bill", "payment", "charge"],
      "response": "Let me check your billing information..."
    }
  }
}
```

## 📊 Dashboard Features

- **Real-time Call Monitoring** - See active calls
- **Analytics** - Call volume, duration, resolution rates
- **Transcripts** - Full conversation history
- **Customer Management** - View and edit customer data
- **Settings** - Configure AI behavior and responses

## 🧪 Testing

Test with a SIP softphone (Zoiper, Linphone, etc.):

```
SIP Server: localhost:5060
Username: 6001
Password: 6001
```

Or use the test script:

```bash
python scripts/test_call.py
```

## 🛠️ Tech Stack

- **VoIP**: Asterisk 20
- **Backend**: Python 3.11, FastAPI
- **AI**: Whisper (ASR), Piper (TTS), LLaMA/Qwen (LLM)
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Frontend**: React 18
- **Containerization**: Docker

## 📈 Roadmap

- [ ] Outbound calling capability
- [ ] Multi-tenant support
- [ ] Advanced analytics with ML insights
- [ ] Integration with CRM systems
- [ ] Voice biometrics for authentication
- [ ] Real-time sentiment analysis

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

**Mouaadh W**  
GitHub: @MouaadhW

## 🙏 Acknowledgments

- Asterisk Project
- OpenAI Whisper
- Piper TTS
- FastAPI
- React

---

Need help? Open an issue or check the documentation.
