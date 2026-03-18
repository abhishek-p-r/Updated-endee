#!/usr/bin/env python
"""Better debugging"""
import requests
import json

print("Testing backend...\n")

try:
    r = requests.post(
        'http://localhost:8000/chat',
        json={'question': 'hello'},
        timeout=10
    )
    
    print(f"Status: {r.status_code}")
    print(f"Headers: {dict(r.headers)}")
    print(f"Response Length: {len(r.text)}")
    print(f"Response Text: {repr(r.text[:200])}")
    
    if r.text:
        try:
            data = r.json()
            print(f"\n✅ Parsed JSON:")
            print(json.dumps(data, indent=2))
        except Exception as je:
            print(f"\n❌ JSON Parse Error: {je}")
            print(f"Raw Response: {r.text}")

except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"❌ Timeout: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
