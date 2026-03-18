#!/usr/bin/env python
"""Direct test of chat function"""
import sys
sys.path.insert(0, 'C:\\Users\\abhis\\tap\\v03')

print("Direct function test...\n")

try:
    from backend.main import chat, QuestionRequest
    import asyncio
    
    # Test the chat function directly
    request = QuestionRequest(question="hello")
    result = asyncio.run(chat(request))
    
    print("Direct call result:")
    print(result)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
