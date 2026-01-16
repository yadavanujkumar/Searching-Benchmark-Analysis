"""
Main benchmark runner for Search ROI Auditor.
This script orchestrates the entire benchmarking process.
"""
import os
import sys
import json
import time
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data'))

from indexing import ElasticsearchIndexer, QdrantIndexer
from evaluation import AccuracyEvaluator
from cost_tracking import CostLogger, HybridSearchCostTracker
from sample_data import generate_sample_dataset, generate_test_queries


class BenchmarkRunner:
    """Main benchmark orchestrator."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.es_indexer = None
        self.qdrant_indexer = None
        self.evaluator = AccuracyEvaluator()
        self.cost_tracker = HybridSearchCostTracker()
        
        self.results = []
        self.indexing_results = {}
        
    def setup_indexers(self):
        """Initialize and connect to search engines."""
        print("Setting up indexers...")
        
        # Elasticsearch
        es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.es_indexer = ElasticsearchIndexer(host=es_host, port=es_port)
        
        # Qdrant
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_indexer = QdrantIndexer(host=qdrant_host, port=qdrant_port)
        
        print("✓ Indexers initialized")
    
    def index_data(self, documents):
        """Index data into both search engines."""
        print("\n=== INDEXING PHASE ===")
        
        # Index in Elasticsearch
        print("\n1. Indexing in Elasticsearch...")
        try:
            if self.es_indexer.connect():
                print("  Connected to Elasticsearch")
                self.es_indexer.create_index()
                print("  Index created")
                
                es_stats = self.es_indexer.index_documents(documents)
                self.indexing_results["Elasticsearch"] = es_stats
                
                print(f"  ✓ Indexed {es_stats['documents_indexed']} documents")
                print(f"    - Duration: {es_stats['duration_seconds']:.2f}s")
                print(f"    - Memory: {es_stats['memory_usage_mb']:.2f} MB")
                print(f"    - Storage: {es_stats['storage_usage_mb']:.2f} MB")
            else:
                print("  ✗ Could not connect to Elasticsearch (using mock mode)")
                self.es_indexer = None
        except Exception as e:
            print(f"  ✗ Elasticsearch indexing failed: {e}")
            self.es_indexer = None
        
        # Index in Qdrant
        print("\n2. Indexing in Qdrant (with embeddings)...")
        try:
            if self.qdrant_indexer.connect():
                print("  Connected to Qdrant")
                self.qdrant_indexer.create_collection()
                print("  Collection created")
                
                qdrant_stats = self.qdrant_indexer.index_documents(documents)
                self.indexing_results["Qdrant"] = qdrant_stats
                
                print(f"  ✓ Indexed {qdrant_stats['documents_indexed']} documents")
                print(f"    - Duration: {qdrant_stats['duration_seconds']:.2f}s")
                print(f"    - Memory: {qdrant_stats['memory_usage_mb']:.2f} MB")
                print(f"    - Storage: {qdrant_stats['storage_usage_mb']:.2f} MB")
                print(f"    - Embedding calls: {qdrant_stats['embedding_calls']}")
            else:
                print("  ✗ Could not connect to Qdrant (using mock mode)")
                self.qdrant_indexer = None
        except Exception as e:
            print(f"  ✗ Qdrant indexing failed: {e}")
            self.qdrant_indexer = None
    
    def run_keyword_search_benchmark(self, test_queries):
        """Benchmark keyword search (Elasticsearch)."""
        print("\n=== KEYWORD SEARCH BENCHMARK ===")
        
        if self.es_indexer is None:
            print("Skipping - Elasticsearch not available")
            return
        
        # Create cost logger
        cost_logger = CostLogger()
        
        # Run evaluation
        def search_function(query):
            start_time = time.time()
            results = self.es_indexer.search(query)
            elapsed = time.time() - start_time
            cost_logger.log_lexical_query(elapsed)
            return results
        
        eval_results = self.evaluator.evaluate_search_method(
            test_queries,
            search_function,
            "Elasticsearch (Keyword)"
        )
        
        # Add cost information
        eval_results["cost_breakdown"] = cost_logger.get_cost_breakdown()
        eval_results["total_cost"] = cost_logger.get_total_cost()
        
        self.results.append(eval_results)
        
        print(f"\n✓ Keyword Search Benchmark Complete")
        print(f"  - Avg Faithfulness: {eval_results['avg_faithfulness']:.2%}")
        print(f"  - Avg Relevancy: {eval_results['avg_relevancy']:.2%}")
        print(f"  - Total Cost: ${eval_results['total_cost']:.4f}")
    
    def run_vector_search_benchmark(self, test_queries):
        """Benchmark vector search (Qdrant)."""
        print("\n=== VECTOR SEARCH BENCHMARK ===")
        
        if self.qdrant_indexer is None:
            print("Skipping - Qdrant not available")
            return
        
        # Create cost logger
        cost_logger = CostLogger()
        
        # Run evaluation
        def search_function(query):
            # Log embedding cost for query
            cost_logger.log_embedding_call(tokens=len(query.split()) * 100)
            
            start_time = time.time()
            results = self.qdrant_indexer.search(query)
            elapsed = time.time() - start_time
            cost_logger.log_vector_query(elapsed)
            return results
        
        eval_results = self.evaluator.evaluate_search_method(
            test_queries,
            search_function,
            "Qdrant (Vector)"
        )
        
        # Add cost information
        eval_results["cost_breakdown"] = cost_logger.get_cost_breakdown()
        eval_results["total_cost"] = cost_logger.get_total_cost()
        
        self.results.append(eval_results)
        
        print(f"\n✓ Vector Search Benchmark Complete")
        print(f"  - Avg Faithfulness: {eval_results['avg_faithfulness']:.2%}")
        print(f"  - Avg Relevancy: {eval_results['avg_relevancy']:.2%}")
        print(f"  - Total Cost: ${eval_results['total_cost']:.4f}")
    
    def run_hybrid_search_benchmark(self, test_queries):
        """Benchmark hybrid search (combining keyword and vector)."""
        print("\n=== HYBRID SEARCH BENCHMARK ===")
        
        if self.es_indexer is None or self.qdrant_indexer is None:
            print("Skipping - Both search engines required for hybrid search")
            return
        
        # Create cost logger
        cost_logger = CostLogger()
        
        # Hybrid search function
        def search_function(query):
            # Log embedding cost
            cost_logger.log_embedding_call(tokens=len(query.split()) * 100)
            
            # Get results from both
            start_time = time.time()
            keyword_results = self.es_indexer.search(query, size=5)
            keyword_time = time.time() - start_time
            cost_logger.log_lexical_query(keyword_time)
            
            start_time = time.time()
            vector_results = self.qdrant_indexer.search(query, limit=5)
            vector_time = time.time() - start_time
            cost_logger.log_vector_query(vector_time)
            
            # Combine and deduplicate results
            combined = []
            seen_ids = set()
            
            # Add vector results first (usually better for semantic)
            for result in vector_results:
                if result["id"] not in seen_ids:
                    combined.append(result)
                    seen_ids.add(result["id"])
            
            # Add keyword results
            for result in keyword_results:
                if result["id"] not in seen_ids:
                    combined.append(result)
                    seen_ids.add(result["id"])
            
            return combined[:10]
        
        eval_results = self.evaluator.evaluate_search_method(
            test_queries,
            search_function,
            "Hybrid (Keyword + Vector)"
        )
        
        # Add cost information
        eval_results["cost_breakdown"] = cost_logger.get_cost_breakdown()
        eval_results["total_cost"] = cost_logger.get_total_cost()
        
        self.results.append(eval_results)
        
        print(f"\n✓ Hybrid Search Benchmark Complete")
        print(f"  - Avg Faithfulness: {eval_results['avg_faithfulness']:.2%}")
        print(f"  - Avg Relevancy: {eval_results['avg_relevancy']:.2%}")
        print(f"  - Total Cost: ${eval_results['total_cost']:.4f}")
    
    def save_results(self):
        """Save benchmark results to files."""
        print("\n=== SAVING RESULTS ===")
        
        os.makedirs("data", exist_ok=True)
        
        # Save benchmark results
        with open("data/benchmark_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("✓ Saved benchmark_results.json")
        
        # Save indexing results
        with open("data/indexing_results.json", "w") as f:
            json.dump(self.indexing_results, f, indent=2)
        print("✓ Saved indexing_results.json")
    
    def cleanup(self):
        """Clean up connections."""
        if self.es_indexer:
            self.es_indexer.close()
        if self.qdrant_indexer:
            self.qdrant_indexer.close()
    
    def run(self, num_documents=100, num_queries=100):
        """
        Run complete benchmark.
        
        Args:
            num_documents: Number of documents to index
            num_queries: Number of test queries to run
        """
        print("=" * 60)
        print("SEARCH ROI AUDITOR - BENCHMARK RUNNER")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_indexers()
            
            # Generate data
            print(f"\nGenerating {num_documents} sample documents...")
            documents = generate_sample_dataset(num_documents)
            print(f"✓ Generated {len(documents)} documents")
            
            print(f"\nGenerating {num_queries} test queries...")
            test_queries = generate_test_queries(num_queries)
            print(f"✓ Generated {len(test_queries)} test queries")
            
            # Index data
            self.index_data(documents)
            
            # Run benchmarks
            self.run_keyword_search_benchmark(test_queries)
            self.run_vector_search_benchmark(test_queries)
            self.run_hybrid_search_benchmark(test_queries)
            
            # Save results
            self.save_results()
            
            print("\n" + "=" * 60)
            print("BENCHMARK COMPLETE!")
            print("=" * 60)
            print("\nView results in the dashboard:")
            print("  streamlit run src/dashboard/app.py")
            print("\nResults saved to:")
            print("  - data/benchmark_results.json")
            print("  - data/indexing_results.json")
            
        except KeyboardInterrupt:
            print("\n\n✗ Benchmark interrupted by user")
        except Exception as e:
            print(f"\n\n✗ Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    runner = BenchmarkRunner()
    
    # Run with default parameters
    # Can be adjusted based on requirements
    runner.run(num_documents=100, num_queries=100)


if __name__ == "__main__":
    main()
