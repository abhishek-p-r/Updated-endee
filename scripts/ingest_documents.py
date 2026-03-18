"""
Comprehensive document ingestion script for Endee Vector Database.

This script:
1. Loads .txt files from data directory
2. Splits text into chunks with overlaps
3. Generates embeddings using SentenceTransformers
4. Stores embeddings in Endee vector database
5. Maintains metadata for source tracking
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.endee_client import EndeeClient
from backend.embeddings import EmbeddingService
from backend.config import settings


class DocumentIngestionPipeline:
    """Complete pipeline for ingesting documents into Endee."""
    
    def __init__(
        self,
        endee_url: str = None,
        collection_name: str = None,
        chunk_size: int = 500,
        chunk_overlap: int = 200
    ):
        """Initialize ingestion pipeline.
        
        Args:
            endee_url: Endee server URL
            collection_name: Endee collection name
            chunk_size: Size of text chunks (characters)
            chunk_overlap: Overlap between chunks (characters)
        """
        self.endee_url = endee_url or settings.endee_url
        self.collection_name = collection_name or settings.endee_collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize clients
        self.endee_client = EndeeClient(self.endee_url)
        self.embedding_service = EmbeddingService()
        
        logger.info(f"Initialized ingestion pipeline")
        logger.info(f"  Endee URL: {self.endee_url}")
        logger.info(f"  Collection: {self.collection_name}")
        logger.info(f"  Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
    
    async def verify_endee_connection(self) -> bool:
        """Verify Endee server is accessible.
        
        Returns:
            True if connected, False otherwise
        """
        logger.info("Verifying Endee connection...")
        is_healthy = await self.endee_client.health_check()
        
        if is_healthy:
            logger.info("✓ Successfully connected to Endee server")
            return True
        else:
            logger.error("✗ Failed to connect to Endee server")
            logger.error(f"  Make sure Endee is running on {self.endee_url}")
            return False
    
    async def create_collection(self) -> bool:
        """Create Endee collection for embeddings.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Creating/Verifying collection: {self.collection_name}")
        
        dimension = self.embedding_service.dimension
        success = await self.endee_client.create_collection(dimension)
        
        if success:
            logger.info(f"✓ Collection '{self.collection_name}' ready")
            logger.info(f"  Dimension: {dimension}")
            logger.info(f"  Metric: cosine similarity")
            return True
        else:
            logger.error(f"✗ Failed to create collection")
            return False
    
    def load_txt_files(self, data_dir: str = "data") -> Dict[str, str]:
        """Load all .txt files from directory.
        
        Args:
            data_dir: Directory containing .txt files
            
        Returns:
            Dictionary of {filename: content}
        """
        logger.info(f"Loading documents from {data_dir}/")
        documents = {}
        data_path = Path(data_dir)
        
        if not data_path.exists():
            logger.error(f"✗ Directory not found: {data_dir}")
            logger.info(f"Creating {data_dir} directory...")
            data_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  Added sample documents to {data_dir}/")
            return self._create_sample_documents(data_dir)
        
        txt_files = list(data_path.glob("*.txt"))
        
        if not txt_files:
            logger.warning(f"⚠ No .txt files found in {data_dir}")
            logger.info("Creating sample documents...")
            return self._create_sample_documents(data_dir)
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents[txt_file.name] = content
                    logger.info(f"✓ Loaded: {txt_file.name} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"✗ Error loading {txt_file.name}: {str(e)}")
        
        logger.info(f"✓ Loaded {len(documents)} documents")
        return documents
    
    def split_text_into_chunks(
        self,
        text: str,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks
    
    def process_documents(
        self,
        documents: Dict[str, str]
    ) -> List[Dict]:
        """Process documents into chunks and prepare for embedding.
        
        Args:
            documents: Dictionary of {filename: content}
            
        Returns:
            List of chunk dictionaries with metadata
        """
        logger.info("Processing documents into chunks...")
        chunks_to_process = []
        total_chunks = 0
        
        for source_file, content in documents.items():
            # Split into chunks
            text_chunks = self.split_text_into_chunks(content)
            logger.info(f"  {source_file}: {len(text_chunks)} chunks")
            
            # Create chunk objects with metadata
            for chunk_idx, chunk_text in enumerate(text_chunks):
                chunk_id = f"{source_file.replace('.txt', '')}_{chunk_idx}"
                chunks_to_process.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "source": source_file,
                    "chunk_index": chunk_idx,
                    "timestamp": datetime.now().isoformat()
                })
                total_chunks += 1
        
        logger.info(f"✓ Created {total_chunks} chunks from {len(documents)} documents")
        return chunks_to_process
    
    async def generate_embeddings(
        self,
        chunks: List[Dict]
    ) -> List[Dict]:
        """Generate embeddings for chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of chunks with embeddings
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings in batch
        start_time = time.time()
        embeddings = self.embedding_service.generate_embeddings_batch(texts)
        elapsed = time.time() - start_time
        
        logger.info(f"✓ Generated {len(embeddings)} embeddings in {elapsed:.2f}s")
        logger.info(f"  Speed: {len(embeddings)/elapsed:.1f} chunks/sec")
        
        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        
        return chunks
    
    async def upsert_to_endee(
        self,
        chunks: List[Dict]
    ) -> Tuple[int, int]:
        """Upsert embeddings to Endee database.
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            Tuple of (successful, failed) count
        """
        logger.info(f"Upserting {len(chunks)} vectors to Endee...")
        
        # Prepare vectors for Endee
        vectors = []
        for chunk in chunks:
            vector_obj = {
                "id": chunk["id"],
                "vector": chunk["embedding"],
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "timestamp": chunk["timestamp"]
                }
            }
            vectors.append(vector_obj)
        
        # Upsert in batches
        batch_size = 100
        successful = 0
        failed = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            start_time = time.time()
            
            success = await self.endee_client.upsert_vectors(batch)
            elapsed = time.time() - start_time
            
            if success:
                successful += len(batch)
                logger.info(f"  ✓ Batch {i//batch_size + 1}: {len(batch)} vectors ({elapsed:.2f}s)")
            else:
                failed += len(batch)
                logger.error(f"  ✗ Batch {i//batch_size + 1} failed")
        
        logger.info(f"✓ Upsert complete: {successful} successful, {failed} failed")
        return successful, failed
    
    def _create_sample_documents(self, data_dir: str) -> Dict[str, str]:
        """Create sample documents for demonstration.
        
        Args:
            data_dir: Directory to save samples
            
        Returns:
            Dictionary of sample documents
        """
        samples = {
            "endee_guide.txt": """# Endee Vector Database Guide

Endee is an open-source vector database designed for high-performance semantic search and RAG pipelines.

## Key Features
- Ultra-fast semantic search using cosine similarity
- Efficient vector storage and retrieval
- Metadata filtering for refined search
- Scalable architecture for large datasets
- RESTful HTTP API for easy integration

## How Endee Works
1. Store text as high-dimensional vectors (embeddings)
2. Search by similarity rather than exact keywords
3. Retrieve top-K most similar results
4. Filter by metadata for refined results

## Installation
The Endee database can be installed using:

```bash
chmod +x install.sh run.sh
./install.sh --release --avx2
./run.sh
```

The server will start on http://localhost:8080

## REST API Endpoints
- POST /collections - Create a new collection
- POST /upsert - Store vectors with metadata
- POST /search - Perform semantic similarity search
- DELETE /collections/{name} - Delete a collection
- GET /health - Check server health

## Use Cases
1. Semantic Search - Find similar documents
2. RAG Pipelines - Retrieve context for LLMs
3. Recommendation Systems - Find similar items
4. Question Answering - Match questions to answers
5. Content Discovery - Find related content
""",
            "embeddings_guide.txt": """# Understanding Vector Embeddings

Vector embeddings are numerical representations of text that capture semantic meaning.

## What are Embeddings?
Embeddings convert text into fixed-size vectors of numbers. Similar texts have similar embeddings, allowing machines to compute semantic similarity.

## Embedding Process
1. Input: Text string (e.g., "What is machine learning?")
2. Processing: Model converts text to numbers
3. Output: Vector of 384 dimensions (in our case)

## Popular Embedding Models
1. sentence-transformers/all-MiniLM-L6-v2
   - Dimensions: 384
   - Speed: Fast, suitable for CPU
   - Quality: Good semantic understanding

2. OpenAI text-embedding-3-small
   - Dimensions: 1536
   - Quality: Very high
   - Cost: API pricing

3. Cohere embeddings
   - Dimensions: Configurable
   - Quality: Enterprise-grade
   - Features: Advanced retrieval options

## Why Use Embeddings?
- Enable semantic search beyond keywords
- Support recommendation systems
- Enable RAG for LLMs
- Power similarity matching
- Enable natural language queries

## Key Properties
- Semantic: Similar meaning → similar vectors
- Deterministic: Same text → same vector
- Comparable: Can compute distance between vectors
- Fixed-size: Always same dimension (384)
""",
            "rag_systems.txt": """# RAG (Retrieval Augmented Generation) Systems

RAG combines language models with information retrieval for improved answers.

## How RAG Works
1. User asks a question
2. System retrieves relevant documents from vector database
3. Retrieved documents serve as context
4. LLM generates answer using context
5. Answer is provided with source citations

## RAG Pipeline Components
1. **Document Ingestion**: Load and process documents
2. **Embedding Generation**: Convert text to vectors
3. **Vector Storage**: Store in Endee database
4. **Query Processing**: Convert user question to embedding
5. **Semantic Search**: Find similar documents in Endee
6. **Context Assembly**: Prepare context for LLM
7. **Answer Generation**: Use LLM to generate response
8. **Source Attribution**: Include citations

## Advantages of RAG
- Provides current, factual information
- Reduces hallucination in responses
- Enables knowledge base integration
- Improves answer accuracy
- Allows source attribution
- Scales with knowledge base size

## Real-World Applications
- Customer support automation
- Technical documentation QA
- Research assistance
- Organizational knowledge systems
- Product recommendation engines
"""
        }
        
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        for filename, content in samples.items():
            filepath = Path(data_dir) / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✓ Created sample: {filename}")
        
        return samples
    
    async def run_full_pipeline(self, data_dir: str = "data") -> Dict:
        """Run complete ingestion pipeline.
        
        Args:
            data_dir: Directory with documents
            
        Returns:
            Pipeline execution results
        """
        logger.info("=" * 60)
        logger.info("STARTING DOCUMENT INGESTION PIPELINE")
        logger.info("=" * 60)
        
        results = {
            "start_time": datetime.now().isoformat(),
            "status": "pending",
            "documents_loaded": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "vectors_stored": 0,
            "errors": []
        }
        
        try:
            # Step 1: Verify connection
            if not await self.verify_endee_connection():
                results["status"] = "failed"
                results["errors"].append("Endee connection failed")
                return results
            
            # Step 2: Create collection
            if not await self.create_collection():
                results["status"] = "failed"
                results["errors"].append("Collection creation failed")
                return results
            
            # Step 3: Load documents
            documents = self.load_txt_files(data_dir)
            if not documents:
                results["status"] = "failed"
                results["errors"].append("No documents found")
                return results
            results["documents_loaded"] = len(documents)
            
            # Step 4: Process into chunks
            chunks = self.process_documents(documents)
            results["chunks_created"] = len(chunks)
            
            # Step 5: Generate embeddings
            chunks_with_embeddings = await self.generate_embeddings(chunks)
            results["embeddings_generated"] = len(chunks_with_embeddings)
            
            # Step 6: Upsert to Endee
            successful, failed = await self.upsert_to_endee(chunks_with_embeddings)
            results["vectors_stored"] = successful
            if failed > 0:
                results["errors"].append(f"{failed} vectors failed to store")
            
            results["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        results["end_time"] = datetime.now().isoformat()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Documents loaded: {results['documents_loaded']}")
        logger.info(f"Chunks created: {results['chunks_created']}")
        logger.info(f"Embeddings generated: {results['embeddings_generated']}")
        logger.info(f"Vectors stored: {results['vectors_stored']}")
        if results["errors"]:
            logger.warning(f"Errors: {', '.join(results['errors'])}")
        logger.info("=" * 60)
        
        return results


async def main():
    """Main entry point for document ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into Endee")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing .txt files (default: data/)"
    )
    parser.add_argument(
        "--endee-url",
        default=None,
        help="Endee server URL (default: from env or http://localhost:8080)"
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Endee collection name (default: knowledge_base)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Size of text chunks in characters (default: 500)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks in characters (default: 200)"
    )
    
    args = parser.parse_args()
    
    # Create and run pipeline
    pipeline = DocumentIngestionPipeline(
        endee_url=args.endee_url,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    results = await pipeline.run_full_pipeline(args.data_dir)
    
    # Return appropriate exit code
    if results["status"] == "completed":
        print(f"\n✓ Successfully ingested {results['vectors_stored']} vectors")
        return 0
    else:
        print(f"\n✗ Ingestion failed: {', '.join(results['errors'])}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
