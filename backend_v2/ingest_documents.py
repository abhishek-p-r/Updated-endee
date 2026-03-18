"""
Document Ingestion Script
Loads documents, generates embeddings, and stores in Endee vector database.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import json

from document_processor import DocumentProcessor, Document, DocumentChunk
from openai_embeddings import OpenAIEmbeddingService
from endee_integration import EndeeVectorDB, VectorMetadata, get_endee_client
from openai_embeddings import get_embedding_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """Pipeline for ingesting documents into Endee vector database."""
    
    def __init__(
        self,
        endee_db: EndeeVectorDB,
        embedding_service: OpenAIEmbeddingService,
        chunk_size: int = 512
    ):
        """Initialize ingestion pipeline.
        
        Args:
            endee_db: Endee vector database
            embedding_service: OpenAI embedding service
            chunk_size: Size of text chunks
        """
        self.endee_db = endee_db
        self.embedding_service = embedding_service
        self.processor = DocumentProcessor(chunk_size=chunk_size)
        self.ingested_count = 0
        self.failed_count = 0
    
    async def ingest_document(self, file_path: str) -> bool:
        """Ingest a single document.
        
        Args:
            file_path: Path to document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing: {file_path}")
            
            # Load document
            document = self.processor.load_document(file_path)
            if not document:
                logger.error(f"Failed to load: {file_path}")
                self.failed_count += 1
                return False
            
            # Chunk document
            chunks = self.processor.chunk_document(document)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_service.embed_texts_async(chunk_texts)
            
            # Prepare vectors for storage
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                metadata = VectorMetadata(
                    document_id=document.id,
                    chunk_id=chunk.id,
                    text=chunk.text,
                    source=document.source,
                    chunk_index=chunk.chunk_index,
                    total_chunks=len(chunks),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    metadata={
                        "document_name": document.name,
                        "file_type": document.file_type,
                        "char_count": chunk.char_count,
                        "token_estimate": chunk.token_estimate
                    }
                )
                vectors.append((chunk.id, embedding, metadata))
            
            # Store in Endee
            success = await self.endee_db.store_vectors(vectors)
            
            if success:
                self.ingested_count += 1
                logger.info(f"✓ Successfully ingested: {document.name}")
                return True
            else:
                self.failed_count += 1
                logger.error(f"✗ Failed to store vectors for: {file_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            self.failed_count += 1
            return False
    
    async def ingest_directory(self, directory: str) -> Dict[str, Any]:
        """Ingest all documents from a directory.
        
        Args:
            directory: Directory path
            
        Returns:
            Ingestion report
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                logger.error(f"Directory not found: {directory}")
                return {
                    "success": False,
                    "message": f"Directory not found: {directory}",
                    "ingested": 0,
                    "failed": 0
                }
            
            # Find all documents
            extensions = ['.txt', '.md', '.pdf']
            files = []
            for ext in extensions:
                files.extend(path.glob(f'**/*{ext}'))
            
            logger.info(f"Found {len(files)} documents")
            
            # Ingest each document
            for file_path in files:
                await self.ingest_document(str(file_path))
            
            # Get collection stats
            stats = await self.endee_db.get_collection_stats()
            
            return {
                "success": True,
                "message": f"Ingested {self.ingested_count} documents, {self.failed_count} failed",
                "ingested": self.ingested_count,
                "failed": self.failed_count,
                "total_files": len(files),
                "collection_stats": stats
            }
        
        except Exception as e:
            logger.error(f"Error ingesting directory: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "ingested": self.ingested_count,
                "failed": self.failed_count
            }


async def main():
    """Main ingestion function."""
    
    # Get configuration from environment
    endee_url = os.getenv("ENDEE_URL", "http://localhost:6379")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    data_dir = os.getenv("DATA_DIR", "./data")
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        endee_db = EndeeVectorDB(
            endee_url=endee_url,
            db_name="knowledge_base",
            vector_dimension=1536
        )
        
        # Health check
        is_healthy = await endee_db.health_check()
        if not is_healthy:
            logger.error("Endee server is not responding")
            sys.exit(1)
        
        # Create collection
        await endee_db.create_collection()
        
        # Initialize embedding service
        embedding_service = OpenAIEmbeddingService(api_key=openai_api_key)
        
        # Create ingestion pipeline
        pipeline = DocumentIngestionPipeline(
            endee_db=endee_db,
            embedding_service=embedding_service,
            chunk_size=512
        )
        
        # Ingest documents
        logger.info(f"Starting ingestion from: {data_dir}")
        report = await pipeline.ingest_directory(data_dir)
        
        # Print report
        logger.info("=" * 50)
        logger.info("INGESTION REPORT")
        logger.info("=" * 50)
        logger.info(f"Status: {'✓ Success' if report['success'] else '✗ Failed'}")
        logger.info(f"Documents Ingested: {report['ingested']}")
        logger.info(f"Failed: {report['failed']}")
        if 'collection_stats' in report:
            logger.info(f"Collection Stats: {json.dumps(report['collection_stats'], indent=2)}")
        logger.info("=" * 50)
        
        # Close connection
        await endee_db.close()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
