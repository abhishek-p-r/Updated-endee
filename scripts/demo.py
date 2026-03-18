#!/usr/bin/env python3
"""
Interactive Demo Script for Endee RAG System

Demonstrates the complete workflow:
1. Create sample documents
2. Ingest into vector database
3. Perform semantic search
4. Generate answers with AI
"""

import asyncio
import os
from pathlib import Path
import tempfile

from backend.endee_vector_db import get_endee_client
from backend.openai_client import get_openai_client
from backend.rag_system import get_rag_system
from backend.document_processor import DocumentProcessor


# Sample documents for demo
SAMPLE_DOCUMENTS = {
    "machine_learning.txt": """
Machine Learning is a subset of artificial intelligence that enables systems to learn 
and improve from experience without being explicitly programmed. 

Key concepts in machine learning:

1. Supervised Learning: The model is trained on a labeled dataset. Examples include 
   classification and regression. Common algorithms include decision trees, support 
   vector machines, and neural networks.

2. Unsupervised Learning: The model learns patterns from unlabeled data. This includes 
   clustering (grouping similar items) and dimensionality reduction.

3. Reinforcement Learning: The model learns through interactions with an environment, 
   receiving rewards or penalties for actions.

4. Deep Learning: Uses neural networks with multiple layers to learn representations 
   of data. Extremely powerful for image and natural language processing.

Applications of machine learning include:
- Image recognition and computer vision
- Natural language processing
- Recommendation systems
- Fraud detection
- Autonomous vehicles
- Medical diagnosis
    """,
    
    "python_basics.txt": """
Python is a high-level, interpreted programming language known for its simplicity 
and readability. It is one of the most popular programming languages today.

Python Fundamentals:

1. Variables and Data Types:
   - Integers, floats, strings
   - Lists, tuples, dictionaries, sets
   - Dynamic typing

2. Control Structures:
   - if/elif/else statements
   - for and while loops
   - break, continue statements

3. Functions:
   - Function definition with def
   - Parameters and return values
   - Lambda functions
   - Decorators

4. Object-Oriented Programming:
   - Classes and objects
   - Inheritance and polymorphism
   - Encapsulation

5. Modules and Packages:
   - Importing modules
   - Creating custom modules
   - Using popular packages like NumPy, Pandas, Django

Python is used in:
- Web development (Django, Flask)
- Data analysis (Pandas, NumPy)
- Machine learning (TensorFlow, PyTorch, Scikit-learn)
- Automation and scripting
- Scientific computing
    """,
    
    "data_science.txt": """
Data Science is an interdisciplinary field that combines statistics, programming, 
and domain expertise to extract meaningful insights from data.

The Data Science Workflow:

1. Problem Definition:
   - Understand business requirements
   - Define metrics for success
   - Identify data sources

2. Data Collection and Preparation:
   - Gather relevant data
   - Clean and preprocess data
   - Handle missing values
   - Feature engineering

3. Exploratory Data Analysis (EDA):
   - Analyze data distributions
   - Find patterns and correlations
   - Visualize relationships
   - Generate hypotheses

4. Model Development:
   - Select appropriate algorithms
   - Train models on training data
   - Validate using cross-validation
   - Hyperparameter tuning

5. Evaluation and Validation:
   - Test on held-out test set
   - Calculate performance metrics
   - Compare multiple models
   - Ensure reproducibility

6. Deployment:
   - Package the model
   - Create API/service
   - Monitor performance in production
   - Retrain as needed

Tools Used in Data Science:
- Python (main language)
- R (statistical programming)
- SQL (data querying)
- Jupyter Notebooks (interactive analysis)
- Git (version control)
- Cloud platforms (AWS, GCP, Azure)

Key Skills:
- Programming and software engineering
- Statistics and mathematics
- Domain knowledge
- Communication and visualization
- Problem-solving
    """
}


async def create_sample_documents(temp_dir: str) -> list:
    """Create sample documents for demo."""
    print("\n" + "="*60)
    print("CREATING SAMPLE DOCUMENTS")
    print("="*60)
    
    file_paths = []
    
    for filename, content in SAMPLE_DOCUMENTS.items():
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        file_paths.append(file_path)
        print(f"✓ Created: {filename} ({len(content)} chars)")
    
    print(f"\nTotal documents created: {len(file_paths)}")
    return file_paths


async def demonstrate_ingestion(rag_system, file_paths: list) -> dict:
    """Demonstrate document ingestion."""
    print("\n" + "="*60)
    print("INGESTING DOCUMENTS INTO VECTOR DATABASE")
    print("="*60)
    
    print(f"\nIngesting {len(file_paths)} documents...")
    print("- Generating embeddings...")
    print("- Storing in Endee vector database...")
    
    result = await rag_system.ingest_documents(file_paths)
    
    print("\nIngestion Complete!")
    print(f"✓ Documents processed: {result.get('documents_processed')}")
    print(f"✓ Chunks created: {result.get('chunks_created')}")
    print(f"✓ Vectors stored: {result.get('vectors_stored')}")
    print(f"✓ Time elapsed: {result.get('time_seconds'):.2f}s")
    
    return result


async def demonstrate_retrieval(rag_system, query: str) -> list:
    """Demonstrate semantic search."""
    print("\n" + "="*60)
    print(f"SEMANTIC SEARCH: '{query}'")
    print("="*60)
    
    print("\nSearching vector database...")
    
    results = await rag_system.retrieve(query, top_k=3)
    
    print(f"\nFound {len(results)} relevant documents:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i} (Score: {result.score:.3f})")
        print(f"Text: {result.text[:200]}...")
        print(f"Metadata: {result.metadata.get('title', 'N/A')}\n")
    
    return results


async def demonstrate_answer_generation(rag_system, question: str):
    """Demonstrate QA with answer generation."""
    print("\n" + "="*60)
    print(f"QUESTION: {question}")
    print("="*60)
    
    print("\nProcessing question...")
    print("1. Converting question to embedding...")
    print("2. Searching vector database...")
    print("3. Generating answer with AI...")
    
    response = await rag_system.answer_question(question, top_k=3)
    
    print("\n" + "-"*60)
    print("ANSWER:")
    print("-"*60)
    print(response.answer)
    
    print("\n" + "-"*60)
    print("SOURCES:")
    print("-"*60)
    for i, doc in enumerate(response.retrieved_documents, 1):
        print(f"\n{i}. Score: {doc['score']:.3f}")
        print(f"   Title: {doc['metadata'].get('title', 'N/A')}")
        print(f"   Text: {doc['text'][:150]}...")
    
    print("\n" + "-"*60)
    print("METRICS:")
    print("-"*60)
    print(f"Response time: {response.response_time_ms:.0f}ms")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Relevance score: {response.retrieval_score:.3f}")
    print(f"Model: {response.model}")


async def main():
    """Run the complete demo."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "ENDEE RAG SYSTEM - INTERACTIVE DEMO".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Initialize clients
        print("\n" + "="*60)
        print("INITIALIZING SYSTEM")
        print("="*60)
        
        print("\nConnecting to Endee vector database...")
        endee_db = await get_endee_client()
        
        is_healthy = await endee_db.health_check()
        if not is_healthy:
            print("✗ Endee server is not responding")
            print("Please start Endee: docker run -p 8000:8000 endeeio/endee:latest")
            return
        
        print("✓ Endee connected")
        
        print("\nInitializing OpenAI client...")
        openai_client = get_openai_client()
        print("✓ OpenAI configured")
        
        print("\nInitializing RAG system...")
        rag_system = await get_rag_system(endee_db, openai_client)
        print("✓ RAG system ready")
        
        # Create sample documents
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = await create_sample_documents(temp_dir)
            
            # Ingest documents
            result = await demonstrate_ingestion(rag_system, file_paths)
            
            if not result.get('success'):
                print("\n✗ Ingestion failed")
                return
            
            # Demonstrate semantic search
            search_queries = [
                "What is machine learning?",
                "Python programming basics",
                "Data science workflow"
            ]
            
            for query in search_queries:
                await demonstrate_retrieval(rag_system, query)
            
            # Demonstrate answer generation
            questions = [
                "What are the main types of machine learning?",
                "How is Python used in data science?",
                "What is the data science workflow?"
            ]
            
            for question in questions:
                await demonstrate_answer_generation(rag_system, question)
                print("\n")
        
        # Summary
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nYou have successfully demonstrated:")
        print("✓ Document ingestion into Endee")
        print("✓ Semantic search using vector similarity")
        print("✓ Answer generation with OpenAI GPT-4o-mini")
        print("✓ Source attribution and metrics")
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Start the web interface:")
        print("   streamlit run frontend/app.py")
        print("\n2. Start the API server:")
        print("   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000")
        print("\n3. Upload your own documents and ask questions!")
        print("\n")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
