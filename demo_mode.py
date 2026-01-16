"""
Demo mode for Search ROI Auditor - runs without external services.
Uses mock data and simulated results for demonstration purposes.
"""
import json
import os
import random


def generate_mock_results():
    """Generate mock benchmark results for demo."""
    
    # Mock results for three search methods
    results = []
    
    # Elasticsearch (Keyword)
    results.append({
        "method_name": "Elasticsearch (Keyword)",
        "num_queries": 100,
        "avg_faithfulness": 0.875,
        "avg_relevancy": 0.892,
        "avg_search_time": 0.012,
        "total_time": 1.2,
        "total_cost": 0.0012,
        "cost_breakdown": {
            "total_cost": 0.0012,
            "embedding_cost": 0.0,
            "vector_query_cost": 0.0,
            "lexical_query_cost": 0.0012,
            "embedding_calls": 0,
            "vector_queries": 0,
            "lexical_queries": 100,
            "total_compute_time": 1.2
        }
    })
    
    # Qdrant (Vector)
    results.append({
        "method_name": "Qdrant (Vector)",
        "num_queries": 100,
        "avg_faithfulness": 0.923,
        "avg_relevancy": 0.941,
        "avg_search_time": 0.045,
        "total_time": 4.5,
        "total_cost": 0.0523,
        "cost_breakdown": {
            "total_cost": 0.0523,
            "embedding_cost": 0.0500,
            "vector_query_cost": 0.0023,
            "lexical_query_cost": 0.0,
            "embedding_calls": 100,
            "vector_queries": 100,
            "lexical_queries": 0,
            "total_compute_time": 4.5
        }
    })
    
    # Hybrid
    results.append({
        "method_name": "Hybrid (Keyword + Vector)",
        "num_queries": 100,
        "avg_faithfulness": 0.948,
        "avg_relevancy": 0.956,
        "avg_search_time": 0.057,
        "total_time": 5.7,
        "total_cost": 0.0535,
        "cost_breakdown": {
            "total_cost": 0.0535,
            "embedding_cost": 0.0500,
            "vector_query_cost": 0.0023,
            "lexical_query_cost": 0.0012,
            "embedding_calls": 100,
            "vector_queries": 100,
            "lexical_queries": 100,
            "total_compute_time": 5.7
        }
    })
    
    return results


def generate_mock_indexing_results():
    """Generate mock indexing results."""
    
    return {
        "Elasticsearch": {
            "success_count": 100,
            "failed_count": 0,
            "duration_seconds": 2.34,
            "memory_usage_mb": 45.67,
            "storage_usage_mb": 12.34,
            "documents_indexed": 100
        },
        "Qdrant": {
            "success_count": 100,
            "failed_count": 0,
            "duration_seconds": 125.89,
            "memory_usage_mb": 234.56,
            "storage_usage_mb": 89.12,
            "documents_indexed": 100,
            "embedding_calls": 100
        }
    }


def main():
    """Run demo mode."""
    print("=" * 60)
    print("SEARCH ROI AUDITOR - DEMO MODE")
    print("=" * 60)
    print("\n⚠️  Running in DEMO MODE with mock data")
    print("For real benchmarks, set up Elasticsearch, Qdrant, and OpenAI API key\n")
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Generate and save mock results
    print("Generating mock benchmark results...")
    results = generate_mock_results()
    
    with open("data/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✓ Saved benchmark_results.json")
    
    print("\nGenerating mock indexing results...")
    indexing_results = generate_mock_indexing_results()
    
    with open("data/indexing_results.json", "w") as f:
        json.dump(indexing_results, f, indent=2)
    print("✓ Saved indexing_results.json")
    
    print("\n" + "=" * 60)
    print("DEMO DATA GENERATED!")
    print("=" * 60)
    print("\nView results in the dashboard:")
    print("  streamlit run src/dashboard/app.py")
    print("\nResults saved to:")
    print("  - data/benchmark_results.json")
    print("  - data/indexing_results.json")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
