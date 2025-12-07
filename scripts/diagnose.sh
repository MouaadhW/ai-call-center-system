#!/bin/bash

echo "=== AI Call Center Diagnostics ==="
echo ""

echo "1. Docker Containers:"
docker-compose ps
echo ""

echo "2. Asterisk Status:"
docker exec asterisk asterisk -rx "core show version"
echo ""

echo "3. SIP Endpoints:"
docker exec asterisk asterisk -rx "pjsip show endpoints"
echo ""

echo "4. SIP Transports:"
docker exec asterisk asterisk -rx "pjsip show transports"
echo ""

echo "5. Network Info:"
docker network inspect ai-call-center-system_callcenter | grep -A 5 "Containers"
echo ""

echo "6. Port Mappings:"
docker port asterisk
docker port backend
echo ""

echo "7. Backend Health:"
curl -s http://localhost:8000/health
echo ""

echo "8. AGI Connection Test:"
# Needs to be run inside the container to test internal connectivity
docker exec asterisk sh -c "timeout 2 telnet backend 4573 2>&1" || echo "Connection Failed"
echo ""

echo "=== End Diagnostics ==="
