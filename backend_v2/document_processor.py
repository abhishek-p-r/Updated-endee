"""
Document Processing Module
Handles loading, parsing, and chunking of documents.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib

import markdown
from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a processed document."""
    id: str
    name: str
    path: str
    content: str
    source: str
    created_at: str
    file_type: str
    size: int


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    id: str
    document_id: str
    chunk_index: int
    text: str
    char_count: int
    token_estimate: int


class DocumentProcessor:
    """Process and chunk documents for embedding storage.
    
    Supports:
    - Plain text (.txt)
    - Markdown (.md)
    - PDF (.pdf)
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize document processor.
        
        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"Document processor initialized (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate unique document ID based on file path and content.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Unique document ID
        """
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"doc_{file_hash[:12]}"
    
    def load_txt_file(self, file_path: str) -> Document:
        """Load and parse a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Document object
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = self._generate_document_id(file_path)
            file_size = os.path.getsize(file_path)
            
            document = Document(
                id=doc_id,
                name=Path(file_path).stem,
                path=file_path,
                content=content,
                source=file_path,
                created_at=datetime.now().isoformat(),
                file_type="text",
                size=file_size
            )
            
            logger.info(f"Loaded text file: {Path(file_path).name} ({file_size} bytes)")
            return document
        
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise
    
    def load_markdown_file(self, file_path: str) -> Document:
        """Load and parse a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Document object
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = self._generate_document_id(file_path)
            file_size = os.path.getsize(file_path)
            
            # Parse markdown headers and structure
            html = markdown.markdown(content)
            
            document = Document(
                id=doc_id,
                name=Path(file_path).stem,
                path=file_path,
                content=content,  # Store original markdown
                source=file_path,
                created_at=datetime.now().isoformat(),
                file_type="markdown",
                size=file_size
            )
            
            logger.info(f"Loaded markdown file: {Path(file_path).name} ({file_size} bytes)")
            return document
        
        except Exception as e:
            logger.error(f"Error loading markdown file {file_path}: {str(e)}")
            raise
    
    def load_pdf_file(self, file_path: str) -> Document:
        """Load and parse a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Document object
        """
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                content += f"\n--- Page {page_num + 1} ---\n{text}"
            
            doc_id = self._generate_document_id(file_path)
            file_size = os.path.getsize(file_path)
            
            document = Document(
                id=doc_id,
                name=Path(file_path).stem,
                path=file_path,
                content=content.strip(),
                source=file_path,
                created_at=datetime.now().isoformat(),
                file_type="pdf",
                size=file_size
            )
            
            logger.info(f"Loaded PDF file: {Path(file_path).name} ({len(pdf_reader.pages)} pages)")
            return document
        
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {str(e)}")
            raise
    
    def load_document(self, file_path: str) -> Optional[Document]:
        """Load a document based on file type.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document object or None if unsupported type
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.txt':
            return self.load_txt_file(file_path)
        elif file_ext == '.md':
            return self.load_markdown_file(file_path)
        elif file_ext == '.pdf':
            return self.load_pdf_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return None
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into chunks.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of document chunks
        """
        try:
            chunks = []
            content = document.content
            
            # Split by newlines first for better semantic boundaries
            paragraphs = content.split('\n\n')
            
            current_chunk = ""
            chunk_index = 0
            
            for paragraph in paragraphs:
                # If adding paragraph exceeds chunk size, save current chunk
                if len(current_chunk) + len(paragraph) > self.chunk_size:
                    if current_chunk.strip():
                        chunk_id = f"{document.id}_chunk_{chunk_index}"
                        chunk = DocumentChunk(
                            id=chunk_id,
                            document_id=document.id,
                            chunk_index=chunk_index,
                            text=current_chunk.strip(),
                            char_count=len(current_chunk),
                            token_estimate=len(current_chunk) // 4  # Rough estimate
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    # Add overlap
                    current_chunk = current_chunk[-self.chunk_overlap:] + paragraph
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
            
            # Add final chunk
            if current_chunk.strip():
                chunk_id = f"{document.id}_chunk_{chunk_index}"
                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    chunk_index=chunk_index,
                    text=current_chunk.strip(),
                    char_count=len(current_chunk),
                    token_estimate=len(current_chunk) // 4
                )
                chunks.append(chunk)
            
            logger.info(f"Chunked document '{document.name}' into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            raise
    
    def load_documents_from_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """Load all documents from a directory.
        
        Args:
            directory: Directory path
            extensions: File extensions to load (default: .txt, .md, .pdf)
            
        Returns:
            List of loaded documents
        """
        if extensions is None:
            extensions = ['.txt', '.md', '.pdf']
        
        documents = []
        path = Path(directory)
        
        for file_path in path.glob('**/*'):
            if file_path.suffix.lower() in extensions:
                try:
                    doc = self.load_document(str(file_path))
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Loaded {len(documents)} documents from {directory}")
        return documents


# Helper functions
def load_single_document(file_path: str, chunk_size: int = 512) -> tuple[Document, List[DocumentChunk]]:
    """Load and chunk a single document.
    
    Args:
        file_path: Path to document
        chunk_size: Chunk size in characters
        
    Returns:
        Tuple of (Document, list of chunks)
    """
    processor = DocumentProcessor(chunk_size=chunk_size)
    document = processor.load_document(file_path)
    chunks = processor.chunk_document(document)
    return document, chunks


def load_directory_documents(
    directory: str,
    chunk_size: int = 512
) -> tuple[List[Document], List[DocumentChunk]]:
    """Load and chunk all documents in a directory.
    
    Args:
        directory: Directory path
        chunk_size: Chunk size in characters
        
    Returns:
        Tuple of (list of documents, list of all chunks)
    """
    processor = DocumentProcessor(chunk_size=chunk_size)
    documents = processor.load_documents_from_directory(directory)
    all_chunks = []
    
    for doc in documents:
        chunks = processor.chunk_document(doc)
        all_chunks.extend(chunks)
    
    return documents, all_chunks
