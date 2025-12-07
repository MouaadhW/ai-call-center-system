FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    portaudio19-dev \
    python3-dev \
    git \
    libsndfile1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install CPU-only PyTorch (Fast download: ~200MB vs 2.5GB)
RUN pip install torch==2.1.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Whisper model will be downloaded on first use

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/recordings /app/data

# Expose ports
EXPOSE 8000 4573

# Run application
CMD ["python", "main.py"]
