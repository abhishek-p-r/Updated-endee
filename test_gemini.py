#!/usr/bin/env python
"""Debug Gemini API issues"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Gemini API...\n")

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"1. API Key set: {'✅ Yes' if api_key else '❌ No'}")
if api_key:
    print(f"   Key (first 20 chars): {api_key[:20]}...")

# Try importing and initializing
print("\n2. Initializing Gemini client...")
try:
    import google.generativeai as genai
    print("   ✅ google.generativeai imported")
    
    genai.configure(api_key=api_key)
    print("   ✅ genai configured")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("   ✅ Model created")
    
    # Try generating response
    print("\n3. Testing response generation...")
    response = model.generate_content("What is 2+2?")
    print(f"   Response type: {type(response)}")
    print(f"   Response text: {response.text[:100] if hasattr(response, 'text') else 'No text attribute'}")
    print("   ✅ Response generated successfully!")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n✅ Gemini test complete!")
