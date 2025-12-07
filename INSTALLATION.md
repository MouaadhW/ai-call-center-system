# 📦 Installation Guide

Complete step-by-step installation instructions for the AI Call Center System.

## System Requirements

### Minimum

- **OS**: Linux (Ubuntu 20.04+), macOS, Windows with WSL2
- **RAM**: 4GB
- **CPU**: 2 cores
- **Storage**: 10GB free space
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Recommended

- **RAM**: 8GB+
- **CPU**: 4+ cores
- **GPU**: NVIDIA GPU with CUDA (optional, for faster ASR)

---

## Step 1: Install Dependencies

### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Python
sudo apt install python3.11 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### macOS

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# Install Python
brew install python@3.11

# Install Node.js
brew install node
```

## Step 2: Clone Repository

```bash
git clone /ai-call-center-system.git
cd ai-call-center-system
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Important settings to configure:

```env
# Company information
COMPANY_NAME="Your Company Name"
COMPANY_PHONE="+1234567890"

# LLM Configuration (if using Ollama)
LLM_MODEL=llama3.2:3b
LLM_API_URL=http://localhost:11434

# Whisper Model (base, small, medium, large)
WHISPER_MODEL=base
```

## Step 4: Install Local LLM (Optional but Recommended)

### Option A: Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2:3b

# Start Ollama service
ollama serve
```

### Option B: Use OpenAI API

Edit `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

## Step 5: Build and Start Services

```bash
# Build all containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:

```
NAME        IMAGE                      STATUS
asterisk    ai-call-center-asterisk    Up
backend     ai-call-center-backend     Up
dashboard   ai-call-center-dashboard   Up
```

## Step 6: Initialize Database

```bash
# Run database initialization
docker exec -it backend python -m db.init_db

# Verify tables created
docker exec -it backend python -c "from db.database import engine; from db.models import Base; print(Base.metadata.tables.keys())"
```

## Step 7: Verify Installation

### Check Asterisk

```bash
docker exec -it asterisk asterisk -rx "core show version"
docker exec -it asterisk asterisk -rx "pjsip show endpoints"
```

### Check Backend API

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy", "version": "1.0.0"}
```

### Check Dashboard

Open browser: http://localhost:3000

## Step 8: Configure SIP Softphone

Install a SIP client (Zoiper, Linphone, MicroSIP):

Configuration:
```
Server: localhost (or your server IP)
Port: 5060
Username: 6001
Password: 6001
Transport: UDP
```

## Step 9: Test First Call

1. Open your SIP softphone
2. Register with credentials above
3. Call extension **100**
4. You should hear the AI agent greeting

## Troubleshooting

### Asterisk won't start

```bash
# Check logs
docker logs asterisk

# Common fix: port conflict
sudo lsof -i :5060
# Kill conflicting process or change port
```

### Backend can't connect to Asterisk

```bash
# Verify network
docker network inspect ai-call-center-system_callcenter

# Restart services
docker-compose restart
```

### Whisper model download fails

```bash
# Manually download
docker exec -it backend python -c "import whisper; whisper.load_model('base')"
```

### Dashboard won't load

```bash
# Check backend API
curl http://localhost:8000/api/calls

# Rebuild dashboard
docker-compose build dashboard
docker-compose up -d dashboard
```

## Next Steps

1. [Quick Start Guide](README.md#quick-start) - Make your first call
2. Testing Guide - Comprehensive testing
3. Configure knowledge base: `backend/knowledge/company_kb.json`
4. Add custom intents in `backend/agent/intent_classifier.py`

## Uninstallation

```bash
# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker rmi $(docker images 'ai-call-center*' -q)
```
