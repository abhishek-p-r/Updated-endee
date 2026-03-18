#!/usr/bin/env python
"""Debug API response"""
import time
import requests

print("Debugging API response...\n")
time.sleep(2)

try:
    r = requests.post('http://localhost:8000/chat', json={'question': 'hello'}, timeout=5)
    print(f"Status Code: {r.status_code}")
    print(f"Headers: {r.headers}")
    print(f"Raw Response: {r.text[:500]}")
    print(f"\nTrying to parse JSON...")
    data = r.json()
    print(f"Parsed JSON: {data}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
