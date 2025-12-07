#!/usr/bin/env python3
"""
Test script for AI Call Center
Simulates a call to test the system
"""

import socket
import time
import sys

def test_agi_connection():
    """Test AGI server connection"""
    print("🔌 Testing AGI server connection...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 4573))
        print("✅ AGI server is reachable")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ AGI server connection failed: {e}")
        return False

def test_api_connection():
    """Test API server connection"""
    print("🔌 Testing API server connection...")
    
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is healthy")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API server connection failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("💾 Testing database connection...")
    
    try:
        import requests
        response = requests.get('http://localhost:8000/api/customers', timeout=5)
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Database accessible ({len(customers)} customers found)")
            return True
        else:
            print(f"❌ Database query failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_asterisk():
    """Test Asterisk connection"""
    print("📞 Testing Asterisk SIP server...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(b"OPTIONS sip:test@localhost SIP/2.0\r\n\r\n", ('localhost', 5060))
        data, addr = sock.recvfrom(1024)
        print("✅ Asterisk SIP server is responding")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Asterisk test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AI Call Center System - Test Suite")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests
    results.append(("API Server", test_api_connection()))
    results.append(("Database", test_database()))
    results.append(("AGI Server", test_agi_connection()))
    results.append(("Asterisk SIP", test_asterisk()))
    
    # Print summary
    print()
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed! System is ready.")
        print()
        print("Next steps:")
        print("  1. Configure a SIP softphone")
        print("  2. Register with: localhost:5060, user: 6001, pass: 6001")
        print("  3. Call extension 100 to test the AI agent")
        print("  4. View dashboard at http://localhost:3000")
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
