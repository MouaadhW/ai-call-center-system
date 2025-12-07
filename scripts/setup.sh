#!/bin/bash

echo "=========================================="
echo "AI Call Center System - Setup Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Build Docker images
echo ""
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Initialize database
echo ""
echo "💾 Initializing database..."
docker exec -it backend python -m db.init_db

# Check service status
echo ""
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🌐 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📞 Asterisk SIP: localhost:5060"
echo ""
echo "📖 Next steps:"
echo "  1. Configure your SIP softphone (user: 6001, pass: 6001)"
echo "  2. Call extension 100 to test the AI agent"
echo "  3. View the dashboard at http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "  - README.md - Project overview"
echo "  - INSTALLATION.md - Detailed installation guide"
echo "  - QUICKSTART.md - Quick start guide"
echo "  - TESTING.md - Testing procedures"
echo ""
