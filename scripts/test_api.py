"""Test utility for the Endee AI Knowledge Assistant API."""
import requests
import json
import sys
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
TIMEOUT = 30


class TestClient:
    """Test client for API testing."""
    
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
        self.session_id = "test_session"
        self.test_results = []
    
    def test_health(self) -> bool:
        """Test health endpoint."""
        print("\n🏥 Testing Health Endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Status: {data.get('status')}")
                print(f"  ✓ Service: {data.get('service')}")
                print(f"  ✓ Endee Connected: {data.get('endee_connected')}")
                self.test_results.append(("Health Check", True, None))
                return True
            else:
                print(f"  ✗ Status: {response.status_code}")
                self.test_results.append(("Health Check", False, response.text))
                return False
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.test_results.append(("Health Check", False, str(e)))
            return False
    
    def test_ask_question(self, question: str = "What is a vector database?") -> bool:
        """Test ask question endpoint."""
        print(f"\n❓ Testing Ask Question Endpoint...")
        print(f"  Question: {question}")
        
        try:
            payload = {
                "question": question,
                "session_id": self.session_id,
                "use_conversation_history": True
            }
            
            response = requests.post(
                f"{self.base_url}/ask",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print(f"  ✓ Answer generated successfully")
                    print(f"  ✓ Retrieved documents: {data.get('retrieved_documents_count', 0)}")
                    answer_length = len(data.get('answer', ''))
                    print(f"  ✓ Answer length: {answer_length} characters")
                    
                    self.test_results.append(("Ask Question", True, None))
                    return True
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"  ✗ Error: {error}")
                    self.test_results.append(("Ask Question", False, error))
                    return False
            else:
                print(f"  ✗ Status: {response.status_code}")
                print(f"  ✗ Response: {response.text[:200]}")
                self.test_results.append(("Ask Question", False, response.text))
                return False
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.test_results.append(("Ask Question", False, str(e)))
            return False
    
    def test_ingest_documents(self) -> bool:
        """Test document ingestion endpoint."""
        print("\n📚 Testing Document Ingestion Endpoint...")
        
        try:
            documents = [
                {
                    "text": "Vector databases store and search embeddings efficiently.",
                    "source": "Test Doc 1"
                },
                {
                    "text": "Embeddings are numerical representations of text.",
                    "source": "Test Doc 2"
                }
            ]
            
            payload = {
                "documents": documents,
                "chunk_size": 100,
                "chunk_overlap": 20
            }
            
            response = requests.post(
                f"{self.base_url}/ingest",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print(f"  ✓ Documents ingested: {data.get('documents_ingested', 0)}")
                    print(f"  ✓ Chunks created: {data.get('chunks_created', 0)}")
                    print(f"  ✓ Vectors stored: {data.get('vectors_stored', 0)}")
                    
                    self.test_results.append(("Ingest Documents", True, None))
                    return True
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"  ✗ Error: {error}")
                    self.test_results.append(("Ingest Documents", False, error))
                    return False
            else:
                print(f"  ✗ Status: {response.status_code}")
                self.test_results.append(("Ingest Documents", False, response.text))
                return False
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.test_results.append(("Ingest Documents", False, str(e)))
            return False
    
    def test_chat_history(self) -> bool:
        """Test chat history endpoints."""
        print("\n💬 Testing Chat History Endpoints...")
        
        try:
            # Get history
            response = requests.get(
                f"{self.base_url}/chat/history/{self.session_id}",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                print(f"  ✓ Retrieved {len(messages)} messages from history")
                
                self.test_results.append(("Chat History", True, None))
                return True
            else:
                print(f"  ✗ Status: {response.status_code}")
                self.test_results.append(("Chat History", False, response.text))
                return False
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.test_results.append(("Chat History", False, str(e)))
            return False
    
    def test_conversation_flow(self) -> bool:
        """Test a complete conversation flow."""
        print("\n🔄 Testing Conversation Flow...")
        
        try:
            # Question 1
            q1 = "What is machine learning?"
            print(f"\n  Question 1: {q1}")
            
            response = requests.post(
                f"{self.base_url}/ask",
                json={
                    "question": q1,
                    "session_id": "flow_test"
                },
                timeout=TIMEOUT
            )
            
            if response.status_code != 200 or not response.json().get("success"):
                print("  ✗ First question failed")
                self.test_results.append(("Conversation Flow", False, "Q1 failed"))
                return False
            
            print("  ✓ Received answer to question 1")
            
            # Question 2 (should use conversation history)
            q2 = "Can you elaborate?"
            print(f"\n  Question 2: {q2}")
            
            response = requests.post(
                f"{self.base_url}/ask",
                json={
                    "question": q2,
                    "session_id": "flow_test",
                    "use_conversation_history": True
                },
                timeout=TIMEOUT
            )
            
            if response.status_code != 200 or not response.json().get("success"):
                print("  ✗ Second question failed")
                self.test_results.append(("Conversation Flow", False, "Q2 failed"))
                return False
            
            print("  ✓ Received answer to question 2 (with history)")
            
            # Check history
            response = requests.get(
                f"{self.base_url}/chat/history/flow_test",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                messages = response.json().get('messages', [])
                if len(messages) >= 4:  # 2 questions + 2 answers
                    print(f"  ✓ Conversation history has {len(messages)} messages")
                    self.test_results.append(("Conversation Flow", True, None))
                    return True
                else:
                    print(f"  ✗ Expected 4+ messages, got {len(messages)}")
                    self.test_results.append(("Conversation Flow", False, "Wrong message count"))
                    return False
            else:
                print("  ✗ Failed to retrieve history")
                self.test_results.append(("Conversation Flow", False, "History retrieval failed"))
                return False
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.test_results.append(("Conversation Flow", False, str(e)))
            return False
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        
        for test_name, success, error in self.test_results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{test_name:.<40} {status}")
            if error and not success:
                print(f"  Error: {str(error)[:100]}")
        
        print("=" * 60)
        
        return failed == 0
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n🚀 Starting API Tests")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Wait for backend to be ready
        print("\n⏳ Waiting for backend to be ready...")
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✓ Backend is ready")
                    break
            except:
                pass
            
            if attempt < max_attempts - 1:
                print(f"  Attempt {attempt + 1}/{max_attempts}...")
                time.sleep(2)
        
        # Run tests
        tests = [
            self.test_health,
            self.test_ingest_documents,
            self.test_ask_question,
            self.test_chat_history,
            self.test_conversation_flow,
        ]
        
        for test in tests:
            test()
            time.sleep(1)  # Small delay between tests
        
        # Print results
        self.print_results()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test the Endee AI Knowledge Assistant API"
    )
    parser.add_argument(
        "--url",
        default=BACKEND_URL,
        help=f"Backend URL (default: {BACKEND_URL})"
    )
    parser.add_argument(
        "--test",
        choices=["health", "ingest", "ask", "history", "flow", "all"],
        default="all",
        help="Specific test to run"
    )
    parser.add_argument(
        "--question",
        help="Custom question for ask test"
    )
    
    args = parser.parse_args()
    
    client = TestClient(args.url)
    
    if args.test == "all":
        client.run_all_tests()
    elif args.test == "health":
        client.test_health()
        client.print_results()
    elif args.test == "ingest":
        client.test_ingest_documents()
        client.print_results()
    elif args.test == "ask":
        question = args.question or "What is a vector database?"
        client.test_ask_question(question)
        client.print_results()
    elif args.test == "history":
        client.test_chat_history()
        client.print_results()
    elif args.test == "flow":
        client.test_conversation_flow()
        client.print_results()


if __name__ == "__main__":
    main()
