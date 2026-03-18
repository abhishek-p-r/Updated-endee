#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test enhanced backend with demo mode"""
import time
import requests

print("Waiting 2 seconds...\n")
time.sleep(2)

test_questions = [
    'hello',
    'what can you do',
    'how are you',
    'help'
]

print("=" * 60)
print("TESTING CHATBOT WITH DEMO MODE")
print("=" * 60)

for q in test_questions:
    try:
        r = requests.post('http://localhost:8000/chat', json={'question': q}, timeout=5)
        data = r.json()
        
        print("\nOK QUESTION: " + q)
        print("   Source: " + str(data.get('source')))
        print("   Status: " + str(data.get('status')))
        resp_text = data.get('response', '')
        if len(resp_text) > 80:
            resp_text = resp_text[:80] + "..."
        print("   Response: " + resp_text)
        
    except Exception as e:
        print("\nFAIL: " + str(e)[:50])

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
