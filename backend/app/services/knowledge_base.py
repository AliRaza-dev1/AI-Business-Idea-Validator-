"""
Knowledge Base Service — Manages RAG document indexing and embedding storage in a local SQLite vector store.
"""
import os
import json
import sqlite3
import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vector_store.db")

class RAGService:
    """Manages chunking, embedding generation, vector indexing, and similarity retrieval."""
    
    def __init__(self):
        self.openai_key = settings.openai_api_key
        # Check if the key is default/test key and handle gracefully
        if not self.openai_key or "sk-test" in self.openai_key:
            # Check environment variables
            self.openai_key = os.getenv("OPENAI_API_KEY", "")
        
        self.client = OpenAI(api_key=self.openai_key)
        self.model = "text-embedding-3-small"
        self._init_db()
    
    def _init_db(self):
        """Initialize the local SQLite database for vector storage"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework_name TEXT,
                    chunk_text TEXT,
                    embedding TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            
    def _get_embedding(self, text: str) -> List[float]:
        """Call OpenAI API to generate high-dimensional text embeddings"""
        if not self.openai_key:
            raise RuntimeError(
                "FATAL: OpenAI API key not configured. "
                "Cannot generate embeddings for RAG retrieval. "
                "Please set OPENAI_API_KEY in .env file."
            )
        
        if "sk-test" in self.openai_key or "replace-with-real-key" in self.openai_key:
            raise RuntimeError(
                "FATAL: OpenAI API key is a placeholder (sk-test or 'replace-with-real-key'). "
                "Please update with a real API key from https://platform.openai.com/api-keys"
            )
        
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embeddings API call failed: {str(e)}")
            logger.error(f"API Key (first 10 chars): {self.openai_key[:10]}...")
            logger.error(f"Model: {self.model}")
            raise RuntimeError(
                f"Failed to generate embeddings via OpenAI API: {str(e)}. "
                f"Check: 1) API key validity, 2) Rate limits, 3) Account credits"
            ) from e

    def chunk_and_index_frameworks(self):
        """Index business frameworks from knowledge/ folder into the vector store"""
        knowledge_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")
        if not os.path.exists(knowledge_dir):
            logger.warning(f"Knowledge directory {knowledge_dir} does not exist.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing index to refresh
        cursor.execute("DELETE FROM document_chunks")
        conn.commit()
        
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".txt"):
                framework_name = filename.replace(".txt", "").replace("_", " ").title()
                filepath = os.path.join(knowledge_dir, filename)
                
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Logical chunking by paragraphs/topics
                chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
                
                logger.info(f"Indexing framework: {framework_name} ({len(chunks)} chunks)")
                
                for chunk in chunks:
                    embedding = self._get_embedding(chunk)
                    embedding_json = json.dumps(embedding)
                    
                    cursor.execute(
                        "INSERT INTO document_chunks (framework_name, chunk_text, embedding) VALUES (?, ?, ?)",
                        (framework_name, chunk, embedding_json)
                    )
        conn.commit()
        conn.close()
        logger.info("Knowledge frameworks indexing complete.")

    def search_similarity(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Query vector database for similar chunks using cosine similarity"""
        query_vector = self._get_embedding(query)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT framework_name, chunk_text, embedding FROM document_chunks")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
            
        results = []
        for framework_name, chunk_text, embedding_json in rows:
            try:
                embedding = json.loads(embedding_json)
                similarity = self._cosine_similarity(query_vector, embedding)
                results.append({
                    "framework_name": framework_name,
                    "chunk_text": chunk_text,
                    "similarity": similarity
                })
            except Exception as e:
                logger.error(f"Error computing similarity: {str(e)}")
                continue
        
        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two numeric vectors"""
        a = np_array = vec_a
        b = np_array = vec_b
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

# Lazy initialization of global RAG Service to avoid blocking app startup
_rag_service_instance = None

def get_rag_service():
    """Get or create the RAG service lazily to avoid blocking app startup"""
    global _rag_service_instance
    if _rag_service_instance is None:
        try:
            _rag_service_instance = RAGService()
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            logger.warning("RAG service disabled - analysis will proceed without RAG retrieval")
            # Return a dummy service that doesn't fail
            _rag_service_instance = type('DummyRAGService', (), {
                'search_similarity': lambda self, query, top_k=2: []
            })()
    return _rag_service_instance

# For backward compatibility - this will be a function that can be called
rag_service = None  # Will be set on first import from base_agent

# Create a factory function that returns the initialized service
def create_rag_service():
    return get_rag_service()
