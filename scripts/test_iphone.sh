#!/bin/bash

echo "=========================================="
echo "iPhone Call Test - Diagnostics"
echo "=========================================="
echo ""

PCIP="192.168.1.19"

echo "1. Testing PC Network:"
ping -c 2 $PCIP
echo ""

echo "2. Testing Docker Containers:"
docker-compose ps
echo ""

echo "3. Testing Asterisk SIP Port:"
if command -v nc &> /dev/null; then
  nc -zv $PCIP 5060 2>&1
else
  echo "nc (netcat) not found, skipping port check."
fi
echo ""

echo "4. Testing Backend API:"
curl -s http://$PCIP:8000/health
echo ""

echo "5. Asterisk Endpoints:"
docker exec asterisk asterisk -rx "pjsip show endpoints" 2>/dev/null
echo ""

echo "6. Asterisk Transports:"
docker exec asterisk asterisk -rx "pjsip show transports" 2>/dev/null
echo ""

echo "7. Windows Firewall Rules:"
if command -v powershell.exe &> /dev/null; then
  powershell.exe -Command "Get-NetFirewallRule -DisplayName 'Asterisk' | Select-Object DisplayName, Enabled"
fi
echo ""

echo "=========================================="
echo "iPhone Configuration:"
echo "=========================================="
echo "Domain: $PCIP"
echo "Port: 5060"
echo "Username: 6001"
echo "Password: 6001"
echo "Transport: UDP"
echo ""
echo "Test Extensions:"
echo "  200 - Echo Test"
echo "  100 - AI Agent"
echo "=========================================="
