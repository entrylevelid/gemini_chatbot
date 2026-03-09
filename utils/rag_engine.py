"""
RAG Engine - Retrieval-Augmented Generation Module
Handles document processing, embedding, and retrieval for the chatbot.
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGEngine:
    """
    RAG Engine for document-based question answering.
    Uses ChromaDB for vector storage and SentenceTransformers for embeddings.
    """
    
    def __init__(self, persist_directory: str = "./vector_store"):
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.client = None
        self.collection = None
        self.documents = {}  # Cache for document metadata
        self.is_initialized = False
        
    def initialize(self, api_key: Optional[str] = None):
        """Initialize the RAG engine with embedding model and vector database."""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB with persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.is_initialized = True
            print("✅ RAG Engine initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing RAG Engine: {e}")
            return False
    
    def _generate_document_id(self, content: str, filename: str) -> str:
        """Generate a unique ID for a document based on its content."""
        hash_input = f"{filename}:{content[:500]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
        return chunks
    
    def load_dummy_data(self, data_dir: str = "./data/dummy_data"):
        """Load dummy data JSON files into the knowledge base."""
        if not self.is_initialized:
            print("❌ RAG Engine not initialized")
            return False
        
        try:
            data_path = Path(data_dir)
            if not data_path.exists():
                print(f"❌ Dummy data directory not found: {data_dir}")
                return False
            
            loaded_count = 0
            for json_file in data_path.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process different JSON structures
                if isinstance(data, dict):
                    # Convert dict to text chunks
                    content = self._dict_to_text(data, json_file.stem)
                    self._add_document(content, json_file.name, "dummy_data")
                    loaded_count += 1
                elif isinstance(data, list):
                    # Process list items
                    for item in data:
                        if isinstance(item, dict):
                            content = self._dict_to_text(item, json_file.stem)
                            doc_id = item.get('id', f"{json_file.stem}_{loaded_count}")
                            self._add_document(content, f"{json_file.name}:{doc_id}", "dummy_data")
                            loaded_count += 1
            
            print(f"✅ Loaded {loaded_count} documents from dummy data")
            return True
            
        except Exception as e:
            print(f"❌ Error loading dummy data: {e}")
            return False
    
    def _dict_to_text(self, data: Dict, source: str) -> str:
        """Convert dictionary data to readable text format."""
        text_parts = [f"Source: {source}"]
        
        for key, value in data.items():
            if isinstance(value, list):
                text_parts.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            text_parts.append(f"  - {k}: {v}")
                    else:
                        text_parts.append(f"  - {item}")
            elif isinstance(value, dict):
                text_parts.append(f"{key}:")
                for k, v in value.items():
                    text_parts.append(f"  {k}: {v}")
            else:
                text_parts.append(f"{key}: {value}")
        
        return "\n".join(text_parts)
    
    def _add_document(self, content: str, filename: str, category: str = "uploaded"):
        """Add a document to the vector database."""
        try:
            # Chunk the document
            chunks = self._chunk_text(content)
            
            if not chunks:
                print(f"⚠️  No chunks created for {filename}")
                return False
            
            # Generate embeddings for chunks
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # Generate IDs and metadata
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "source": filename,
                    "category": category,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            
            # Cache document info
            self.documents[filename] = {
                "category": category,
                "chunks": len(chunks)
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding document {filename}: {e}")
            return False
    
    def add_document(self, content: str, filename: str) -> bool:
        """Public method to add a document."""
        if not self.is_initialized:
            return False
        return self._add_document(content, filename, "uploaded")
    
    def remove_document(self, filename: str) -> bool:
        """Remove a document from the vector database."""
        try:
            # Get all IDs that start with the filename
            existing = self.collection.get(
                where={"source": filename}
            )
            
            if existing and existing['ids']:
                self.collection.delete(ids=existing['ids'])
                if filename in self.documents:
                    del self.documents[filename]
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error removing document {filename}: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant document chunks."""
        if not self.is_initialized:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "source": results['metadatas'][0][i]['source'],
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def get_context(self, query: str, max_tokens: int = 1500) -> str:
        """Get relevant context for a query, formatted for the LLM."""
        results = self.search(query, top_k=5)
        
        if not results:
            return ""
        
        context_parts = []
        total_length = 0
        
        for result in results:
            chunk = f"[Source: {result['source']}]\n{result['content']}"
            if total_length + len(chunk) <= max_tokens:
                context_parts.append(chunk)
                total_length += len(chunk)
        
        return "\n\n".join(context_parts)
    
    def get_all_documents(self) -> List[Dict[str, str]]:
        """Get list of all documents in the knowledge base."""
        docs = []
        for filename, info in self.documents.items():
            docs.append({
                "name": filename,
                "category": info['category'],
                "chunks": info['chunks']
            })
        return docs
    
    def clear_all(self):
        """Clear all documents from the knowledge base."""
        try:
            if self.collection:
                self.client.delete_collection("knowledge_base")
                self.collection = self.client.get_or_create_collection(
                    name="knowledge_base",
                    metadata={"hnsw:space": "cosine"}
                )
                self.documents = {}
                print("✅ Knowledge base cleared")
                return True
        except Exception as e:
            print(f"❌ Error clearing knowledge base: {e}")
            return False


# Global instance
rag_engine = RAGEngine()
