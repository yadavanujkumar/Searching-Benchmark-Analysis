"""
Qdrant vector indexing module with memory and storage tracking.
"""
import time
import psutil
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import openai
import os


class QdrantIndexer:
    """Handles Qdrant vector indexing with resource tracking."""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.host = host
        self.port = port
        self.client = None
        self.collection_name = "search_benchmark"
        self.vector_size = 1536  # OpenAI embedding dimension
        self.memory_usage = 0
        self.storage_usage = 0
        self.embedding_calls = 0
        
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def connect(self):
        """Connect to Qdrant."""
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            return True
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            return False
    
    def create_collection(self):
        """Create collection with vector configuration."""
        if self.client is None:
            raise Exception("Client not connected")
        
        # Delete collection if exists
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except:
            pass
        
        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        self.embedding_calls += 1
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index documents with vectors and track resource usage.
        
        Args:
            documents: List of documents to index
            
        Returns:
            Dictionary with indexing stats and resource usage
        """
        if self.client is None:
            raise Exception("Client not connected")
        
        # Track memory before indexing
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        start_time = time.time()
        self.embedding_calls = 0
        
        # Create points with embeddings
        points = []
        for doc in documents:
            # Create text for embedding
            text_to_embed = f"{doc.get('title', '')} {doc.get('content', '')}"
            vector = self.get_embedding(text_to_embed)
            
            point = PointStruct(
                id=hash(doc["id"]) % (2**63),  # Convert string id to int
                vector=vector,
                payload=doc
            )
            points.append(point)
        
        # Upload points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        end_time = time.time()
        
        # Track memory after indexing
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        self.memory_usage = memory_after - memory_before
        
        # Get collection info for storage size
        collection_info = self.client.get_collection(collection_name=self.collection_name)
        # Estimate storage: vectors + payload
        vector_storage = (self.vector_size * 4 * len(documents)) / (1024 * 1024)  # MB (float32)
        self.storage_usage = vector_storage
        
        return {
            "success_count": len(documents),
            "failed_count": 0,
            "duration_seconds": end_time - start_time,
            "memory_usage_mb": self.memory_usage,
            "storage_usage_mb": self.storage_usage,
            "documents_indexed": len(documents),
            "embedding_calls": self.embedding_calls
        }
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents using vector similarity.
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of matching documents
        """
        if self.client is None:
            raise Exception("Client not connected")
        
        # Get query embedding
        query_vector = self.get_embedding(query)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        output = []
        for result in results:
            output.append({
                "id": result.payload["id"],
                "score": result.score,
                "content": result.payload
            })
        
        return output
    
    def close(self):
        """Close the connection."""
        pass  # Qdrant client doesn't require explicit closing
