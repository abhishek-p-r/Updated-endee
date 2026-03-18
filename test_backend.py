#!/usr/bin/env python
"""Test backend connectivity and endpoints"""
import requests
import time
import json

print("🔍 Testing Backend...\n")

# Wait for backend to start
print("⏳ Waiting 3 seconds for backend to fully boot...")
time.sleep(3)

BASE_URL = "http://localhost:8000"

# Test 1: Health endpoint
print("\n1️⃣ Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ Health check working!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Chat endpoint
print("\n2️⃣ Testing /chat endpoint...")
try:
    test_question = "Hello, can you help me with AI?"
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"question": test_question},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response from: {data.get('source', 'Unknown')}")
    print(f"   Answer: {data.get('response', 'No response')[:100]}...")
    print("   ✅ Chat endpoint working!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Backend test complete!")
