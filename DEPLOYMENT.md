# Deployment Guide

## Local Development

```bash
# Clone repository
git clone https://github.com/MouaadhW/ai-call-center-system.git
cd ai-call-center-system

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Initialize database
docker exec -it backend python -m db.init_db

# Access dashboard
open http://localhost:3000
```

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker & Docker Compose
- Domain name (optional)
- SSL certificate (recommended)

### Steps

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

#### 2. Clone and Configure

```bash
git clone https://github.com/MouaadhW/ai-call-center-system.git
cd ai-call-center-system

# Production environment
cp .env.example .env
nano .env  # Configure for production
```

#### 3. Security Configuration

```bash
# Change default passwords in .env
# Set strong database credentials

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5060/udp
sudo ufw enable
```

#### 4. SSL Setup (with Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update docker-compose.yml to use SSL
```

#### 5. Start Production Services

```bash
docker-compose up -d
```

#### 6. Configure SIP Trunk (for real phone numbers)

- Sign up with a SIP provider (Twilio, Vonage, etc.)
- Configure trunk in `docker/asterisk/pjsip.conf`
- Update dialplan in `docker/asterisk/extensions.conf`

### Monitoring

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Monitor resources
docker stats
```

## Backup & Recovery

### Backup

```bash
# Backup database
docker exec backend sqlite3 /app/data/callcenter.db ".backup '/app/data/backup.db'"

# Backup configuration
tar -czf config-backup.tar.gz docker/ backend/knowledge/ .env
```

### Restore

```bash
# Restore database
docker cp backup.db backend:/app/data/callcenter.db

# Restore configuration
tar -xzf config-backup.tar.gz
```

## Scaling

### Horizontal Scaling

- Use load balancer (Nginx, HAProxy)
- Run multiple backend instances
- Shared database (PostgreSQL recommended)

### Vertical Scaling

- Increase Docker resource limits
- Optimize Whisper model size
- Use GPU for ASR/TTS

## Troubleshooting

### Service Won't Start

```bash
docker-compose logs [service-name]
docker-compose restart [service-name]
```

### Database Issues

```bash
docker exec -it backend python -m db.init_db
```

### Asterisk Issues

```bash
docker exec -it asterisk asterisk -rx "core show version"
docker exec -it asterisk asterisk -rx "pjsip show endpoints"
```

## Maintenance

### Updates

```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Log Rotation

Configure in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Support

For production support, open an issue on GitHub or contact the maintainers.
