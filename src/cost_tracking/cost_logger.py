"""
Real-time cost logging module for tracking infrastructure costs.
"""
import time
from typing import Dict, Any, List
from datetime import datetime
import os


class CostLogger:
    """Tracks and calculates costs for search operations."""
    
    def __init__(self):
        # Load cost configuration from environment
        self.embedding_cost_per_1k = float(os.getenv("EMBEDDING_COST_PER_1K", "0.0001"))
        self.vector_db_cost_per_query = float(os.getenv("VECTOR_DB_COST_PER_QUERY", "0.00001"))
        self.lexical_db_cost_per_query = float(os.getenv("LEXICAL_DB_COST_PER_QUERY", "0.000001"))
        
        # Cost tracking
        self.embedding_calls = 0
        self.vector_queries = 0
        self.lexical_queries = 0
        self.compute_time = 0.0
        
        # Detailed logs
        self.cost_logs = []
        
    def log_embedding_call(self, tokens: int = 1000):
        """
        Log an embedding API call.
        
        Args:
            tokens: Number of tokens (default 1000 for average document)
        """
        self.embedding_calls += 1
        cost = (tokens / 1000) * self.embedding_cost_per_1k
        
        self.cost_logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "embedding",
            "tokens": tokens,
            "cost": cost
        })
        
        return cost
    
    def log_vector_query(self, compute_time: float):
        """
        Log a vector database query.
        
        Args:
            compute_time: Time taken for the query in seconds
        """
        self.vector_queries += 1
        self.compute_time += compute_time
        cost = self.vector_db_cost_per_query + (compute_time * 0.00001)  # Additional cost for compute time
        
        self.cost_logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "vector_query",
            "compute_time": compute_time,
            "cost": cost
        })
        
        return cost
    
    def log_lexical_query(self, latency: float):
        """
        Log a lexical database query.
        
        Args:
            latency: Query latency in seconds
        """
        self.lexical_queries += 1
        cost = self.lexical_db_cost_per_query + (latency * 0.000001)  # Additional cost for latency
        
        self.cost_logs.append({
            "timestamp": datetime.now().isoformat(),
            "type": "lexical_query",
            "latency": latency,
            "cost": cost
        })
        
        return cost
    
    def get_total_cost(self) -> float:
        """Calculate total cost from all operations."""
        return sum(log["cost"] for log in self.cost_logs)
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown."""
        embedding_cost = sum(log["cost"] for log in self.cost_logs if log["type"] == "embedding")
        vector_cost = sum(log["cost"] for log in self.cost_logs if log["type"] == "vector_query")
        lexical_cost = sum(log["cost"] for log in self.cost_logs if log["type"] == "lexical_query")
        
        return {
            "total_cost": self.get_total_cost(),
            "embedding_cost": embedding_cost,
            "vector_query_cost": vector_cost,
            "lexical_query_cost": lexical_cost,
            "embedding_calls": self.embedding_calls,
            "vector_queries": self.vector_queries,
            "lexical_queries": self.lexical_queries,
            "total_compute_time": self.compute_time
        }
    
    def reset(self):
        """Reset all cost tracking."""
        self.embedding_calls = 0
        self.vector_queries = 0
        self.lexical_queries = 0
        self.compute_time = 0.0
        self.cost_logs = []
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all cost logs."""
        return self.cost_logs


class HybridSearchCostTracker:
    """Tracks costs for hybrid search combining multiple methods."""
    
    def __init__(self):
        self.cost_logger = CostLogger()
        self.method_costs = {}
        
    def track_search_method(
        self,
        method_name: str,
        search_function,
        query: str,
        embedding_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Track costs for a single search method execution.
        
        Args:
            method_name: Name of the search method
            search_function: Function to execute
            query: Search query
            embedding_tokens: Estimated tokens for embedding
            
        Returns:
            Dictionary with results and costs
        """
        # Create a new cost logger for this method
        method_logger = CostLogger()
        
        # Track based on method type
        start_time = time.time()
        
        if "vector" in method_name.lower() or "qdrant" in method_name.lower():
            # Log embedding call
            method_logger.log_embedding_call(embedding_tokens)
            
            # Execute search
            results = search_function(query)
            elapsed = time.time() - start_time
            
            # Log vector query
            method_logger.log_vector_query(elapsed)
            
        elif "keyword" in method_name.lower() or "elasticsearch" in method_name.lower():
            # Execute search
            results = search_function(query)
            elapsed = time.time() - start_time
            
            # Log lexical query
            method_logger.log_lexical_query(elapsed)
            
        else:
            # Hybrid or other method
            results = search_function(query)
            elapsed = time.time() - start_time
        
        # Store method costs
        self.method_costs[method_name] = method_logger.get_cost_breakdown()
        
        return {
            "method_name": method_name,
            "results": results,
            "cost_breakdown": method_logger.get_cost_breakdown(),
            "execution_time": elapsed
        }
    
    def get_method_comparison(self) -> Dict[str, Any]:
        """Get cost comparison across all methods."""
        return {
            "methods": self.method_costs,
            "total_cost": sum(m["total_cost"] for m in self.method_costs.values())
        }
