"""
Elasticsearch indexing module with memory and storage tracking.
"""
import time
import psutil
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticsearchIndexer:
    """Handles Elasticsearch indexing with resource tracking."""
    
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.host = host
        self.port = port
        self.client = None
        self.index_name = "search_benchmark"
        self.memory_usage = 0
        self.storage_usage = 0
        
    def connect(self):
        """Connect to Elasticsearch."""
        try:
            self.client = Elasticsearch([f"http://{self.host}:{self.port}"])
            return self.client.ping()
        except Exception as e:
            print(f"Failed to connect to Elasticsearch: {e}")
            return False
    
    def create_index(self):
        """Create index with mapping."""
        if self.client is None:
            raise Exception("Client not connected")
        
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
        
        if self.client.indices.exists(index=self.index_name):
            self.client.indices.delete(index=self.index_name)
        
        self.client.indices.create(index=self.index_name, body=mapping)
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index documents and track resource usage.
        
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
        
        # Prepare bulk actions
        actions = [
            {
                "_index": self.index_name,
                "_id": doc["id"],
                "_source": doc
            }
            for doc in documents
        ]
        
        # Bulk index
        success, failed = bulk(self.client, actions, stats_only=True)
        
        # Force refresh to ensure data is searchable
        self.client.indices.refresh(index=self.index_name)
        
        end_time = time.time()
        
        # Track memory after indexing
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        self.memory_usage = memory_after - memory_before
        
        # Get index storage size
        stats = self.client.indices.stats(index=self.index_name)
        self.storage_usage = stats['indices'][self.index_name]['total']['store']['size_in_bytes'] / (1024 * 1024)  # MB
        
        return {
            "success_count": success,
            "failed_count": failed,
            "duration_seconds": end_time - start_time,
            "memory_usage_mb": self.memory_usage,
            "storage_usage_mb": self.storage_usage,
            "documents_indexed": len(documents)
        }
    
    def search(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents using keyword search.
        
        Args:
            query: Search query
            size: Number of results to return
            
        Returns:
            List of matching documents
        """
        if self.client is None:
            raise Exception("Client not connected")
        
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content"]
                }
            },
            "size": size
        }
        
        response = self.client.search(index=self.index_name, body=search_body)
        
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "id": hit['_id'],
                "score": hit['_score'],
                "content": hit['_source']
            })
        
        return results
    
    def close(self):
        """Close the connection."""
        if self.client:
            self.client.close()
