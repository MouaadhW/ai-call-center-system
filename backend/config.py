import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
RECORDINGS_DIR = BASE_DIR / "recordings"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, RECORDINGS_DIR, KNOWLEDGE_DIR]:
    directory.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/callcenter.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Asterisk Configuration
ASTERISK_HOST = os.getenv("ASTERISK_HOST", "asterisk")
ASTERISK_AGI_PORT = int(os.getenv("ASTERISK_AGI_PORT", 4573))

# AI Model Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ASR Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "piper")
TTS_MODEL = os.getenv("TTS_MODEL", "en_US-lessac-medium")
TTS_SPEED = float(os.getenv("TTS_SPEED", 1.0))

# Company Information
COMPANY_NAME = os.getenv("COMPANY_NAME", "AI Call Center")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+1234567890")

# Call Configuration
MAX_CALL_DURATION = int(os.getenv("MAX_CALL_DURATION", 600))  # 10 minutes
SILENCE_TIMEOUT = int(os.getenv("SILENCE_TIMEOUT", 10))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "callcenter.log"

# Dashboard
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 3000))

# Audio Settings
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FORMAT = "wav"

# Knowledge Base
KB_FILE = KNOWLEDGE_DIR / "company_kb.json"

# Feature Flags
ENABLE_RECORDING = os.getenv("ENABLE_RECORDING", "true").lower() == "true"
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
ENABLE_SENTIMENT = os.getenv("ENABLE_SENTIMENT", "false").lower() == "true"
