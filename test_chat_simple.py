#!/usr/bin/env python
"""Quick test of updated backend"""
import time
import requests
import json

print("⏳ Waiting 3 seconds for backend to fully start...")
time.sleep(3)

print("\nTesting /chat endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"question": "Hello, can you help me with AI?"},
        timeout=15
    )
    data = response.json()
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"Source: {data.get('source', 'Unknown')}")
    print(f"Error Type: {data.get('error_type', 'N/A')}")
    print(f"\nResponse (first 300 chars):")
    print(data.get('response', 'No response')[:300])
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete!")
