"""
Configuration module for Search ROI Auditor.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration."""
    host: str = "localhost"
    port: int = 9200
    index_name: str = "search_benchmark"


@dataclass
class QdrantConfig:
    """Qdrant configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "search_benchmark"
    vector_size: int = 1536


@dataclass
class CostConfig:
    """Cost configuration."""
    embedding_cost_per_1k: float = 0.0001
    vector_db_cost_per_query: float = 0.00001
    lexical_db_cost_per_query: float = 0.000001


@dataclass
class BenchmarkConfig:
    """Overall benchmark configuration."""
    num_documents: int = 100
    num_queries: int = 100
    openai_api_key: Optional[str] = None
    
    elasticsearch: ElasticsearchConfig = None
    qdrant: QdrantConfig = None
    cost: CostConfig = None
    
    def __post_init__(self):
        if self.elasticsearch is None:
            self.elasticsearch = ElasticsearchConfig()
        if self.qdrant is None:
            self.qdrant = QdrantConfig()
        if self.cost is None:
            self.cost = CostConfig()
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            elasticsearch=ElasticsearchConfig(
                host=os.getenv("ELASTICSEARCH_HOST", "localhost"),
                port=int(os.getenv("ELASTICSEARCH_PORT", "9200"))
            ),
            qdrant=QdrantConfig(
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", "6333"))
            ),
            cost=CostConfig(
                embedding_cost_per_1k=float(os.getenv("EMBEDDING_COST_PER_1K", "0.0001")),
                vector_db_cost_per_query=float(os.getenv("VECTOR_DB_COST_PER_QUERY", "0.00001")),
                lexical_db_cost_per_query=float(os.getenv("LEXICAL_DB_COST_PER_QUERY", "0.000001"))
            )
        )
