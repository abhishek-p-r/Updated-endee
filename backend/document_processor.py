"""
Document Processing and Text Chunking Module

Handles loading documents from various formats (.txt, .pdf, .md),
cleaning text, chunking into manageable pieces, and generating embeddings.
"""

import logging
import os
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from markdown import markdown
except ImportError:
    markdown = None

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a processed document."""
    id: str
    title: str
    source: str
    content: str
    chunks: List[str]
    metadata: Dict[str, Any]


@dataclass
class TextChunk:
    """Represents a chunk of text for embedding."""
    id: str
    document_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any]


class DocumentProcessor:
    """
    Process documents and convert them into chunks suitable for embedding.
    
    Features:
    - Load .txt, .pdf, .md files
    - Clean and normalize text
    - Intelligent chunking (overlap support)
    - Metadata extraction
    - Batch processing
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target size for each chunk (words)
            chunk_overlap: Overlap between chunks (words)
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        logger.info(
            f"DocumentProcessor initialized "
            f"(chunk_size={chunk_size}, overlap={chunk_overlap})"
        )
    
    def load_txt_file(self, file_path: str) -> str:
        """
        Load text from a .txt file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded .txt file: {file_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error loading .txt file {file_path}: {str(e)}")
            raise
    
    def load_pdf_file(self, file_path: str) -> str:
        """
        Load text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 required for PDF support: pip install PyPDF2")
        
        try:
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    text += f"\n[Page {page_num + 1}]\n"
                    text += page.extract_text()
            
            logger.info(f"Loaded PDF file: {file_path} ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {str(e)}")
            raise
    
    def load_markdown_file(self, file_path: str) -> str:
        """
        Load text from a Markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            File content as string (preserves markdown structure)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded Markdown file: {file_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error loading markdown file {file_path}: {str(e)}")
            raise
    
    def load_document(self, file_path: str) -> str:
        """
        Load document from file (auto-detects format).
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document content
        """
        file_path = str(file_path)
        ext = Path(file_path).suffix.lower()
        
        if ext == '.txt':
            return self.load_txt_file(file_path)
        elif ext == '.pdf':
            return self.load_pdf_file(file_path)
        elif ext in ['.md', '.markdown']:
            return self.load_markdown_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([\.!\?,;:])', r'\1', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Clean text first
        text = self.clean_text(text)
        
        # Split into words
        words = text.split()
        
        if len(words) < self.min_chunk_size:
            return [text] if text else []
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk = ' '.join(words[start_idx:end_idx])
            
            if len(chunk.split()) >= self.min_chunk_size:
                chunks.append(chunk)
            
            # Move start position considering overlap
            start_idx = end_idx - self.chunk_overlap
        
        logger.info(
            f"Chunked text into {len(chunks)} chunks "
            f"(avg size: {sum(len(c.split()) for c in chunks) // len(chunks) if chunks else 0} words)"
        )
        
        return chunks
    
    def process_document(
        self,
        file_path: str,
        document_id: Optional[str] = None
    ) -> Document:
        """
        Process a complete document into chunks.
        
        Args:
            file_path: Path to document file
            document_id: Optional custom document ID
            
        Returns:
            Document object with chunks
        """
        try:
            # Load document
            content = self.load_document(file_path)
            
            # Generate document ID if not provided
            if not document_id:
                file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                document_id = f"doc_{file_hash}"
            
            # Get document metadata
            file_path_obj = Path(file_path)
            title = file_path_obj.stem
            
            # Chunk the content
            chunks = self.chunk_text(content)
            
            # Create document
            document = Document(
                id=document_id,
                title=title,
                source=str(file_path),
                content=content,
                chunks=chunks,
                metadata={
                    "file_name": file_path_obj.name,
                    "file_type": file_path_obj.suffix,
                    "num_chunks": len(chunks),
                    "total_words": len(content.split()),
                    "total_chars": len(content)
                }
            )
            
            logger.info(
                f"Processed document '{title}' into {len(chunks)} chunks "
                f"(ID: {document_id})"
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def process_directory(
        self,
        directory: str,
        pattern: str = "*.txt",
        recursive: bool = True
    ) -> List[Document]:
        """
        Process all documents in a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match (default: *.txt)
            recursive: Search recursively
            
        Returns:
            List of Document objects
        """
        try:
            dir_path = Path(directory)
            
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            logger.info(f"Found {len(files)} files in {directory}")
            
            documents = []
            for file_path in files:
                try:
                    doc = self.process_document(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Skipped {file_path}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing directory {directory}: {str(e)}")
            raise
    
    def get_text_chunks(self, document: Document) -> List[TextChunk]:
        """
        Convert Document into TextChunk objects for embedding.
        
        Args:
            document: Document to convert
            
        Returns:
            List of TextChunk objects
        """
        chunks = []
        
        for idx, text in enumerate(document.chunks):
            chunk = TextChunk(
                id=f"{document.id}_chunk_{idx}",
                document_id=document.id,
                text=text,
                chunk_index=idx,
                metadata={
                    **document.metadata,
                    "title": document.title,
                    "chunk_index": idx,
                    "source": document.source
                }
            )
            chunks.append(chunk)
        
        return chunks


# Convenience function
def process_documents_batch(
    file_paths: List[str],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[TextChunk]:
    """
    Process a batch of documents into text chunks.
    
    Args:
        file_paths: List of file paths
        chunk_size: Chunk size in words
        chunk_overlap: Overlap in words
        
    Returns:
        List of TextChunk objects
    """
    processor = DocumentProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    all_chunks = []
    
    for file_path in file_paths:
        try:
            doc = processor.process_document(file_path)
            chunks = processor.get_text_chunks(doc)
            all_chunks.extend(chunks)
        except Exception as e:
            logger.warning(f"Skipped {file_path}: {str(e)}")
            continue
    
    logger.info(f"Processed {len(all_chunks)} total chunks from {len(file_paths)} files")
    return all_chunks
