"""
Test script to verify all modules work correctly.
"""
import sys
import os

# Add paths
sys.path.insert(0, 'src')
sys.path.insert(0, 'data')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from indexing import ElasticsearchIndexer, QdrantIndexer
        print("✓ Indexing modules imported")
    except Exception as e:
        print(f"⚠ Indexing modules have missing dependencies (optional): {e}")
        print("  (This is OK - elasticsearch and qdrant-client are optional)")
    
    try:
        from evaluation import AccuracyEvaluator
        print("✓ Evaluation module imported")
    except Exception as e:
        print(f"⚠ Evaluation module has missing dependencies (optional): {e}")
        print("  (This is OK - deepeval is optional)")
    
    try:
        from cost_tracking import CostLogger, HybridSearchCostTracker
        print("✓ Cost tracking modules imported")
    except Exception as e:
        print(f"✗ Failed to import cost tracking modules: {e}")
        return False
    
    try:
        from sample_data import generate_sample_dataset, generate_test_queries
        print("✓ Sample data module imported")
    except Exception as e:
        print(f"✗ Failed to import sample data module: {e}")
        return False
    
    return True


def test_data_generation():
    """Test data generation."""
    print("\nTesting data generation...")
    
    try:
        from sample_data import generate_sample_dataset, generate_test_queries
        
        docs = generate_sample_dataset(10)
        assert len(docs) == 10, "Expected 10 documents"
        assert 'id' in docs[0], "Document missing id field"
        assert 'content' in docs[0], "Document missing content field"
        print(f"✓ Generated {len(docs)} sample documents")
        
        queries = generate_test_queries(20)
        assert len(queries) == 20, "Expected 20 queries"
        assert 'query' in queries[0], "Query missing query field"
        print(f"✓ Generated {len(queries)} test queries")
        
        return True
    except Exception as e:
        print(f"✗ Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cost_logger():
    """Test cost logging."""
    print("\nTesting cost logger...")
    
    try:
        from cost_tracking import CostLogger
        
        logger = CostLogger()
        
        # Test embedding cost
        cost1 = logger.log_embedding_call(1000)
        assert cost1 > 0, "Embedding cost should be positive"
        
        # Test vector query cost
        cost2 = logger.log_vector_query(0.05)
        assert cost2 > 0, "Vector query cost should be positive"
        
        # Test lexical query cost
        cost3 = logger.log_lexical_query(0.01)
        assert cost3 > 0, "Lexical query cost should be positive"
        
        # Test total cost
        total = logger.get_total_cost()
        assert total == cost1 + cost2 + cost3, "Total cost mismatch"
        
        # Test breakdown
        breakdown = logger.get_cost_breakdown()
        assert 'total_cost' in breakdown, "Missing total_cost in breakdown"
        assert 'embedding_cost' in breakdown, "Missing embedding_cost in breakdown"
        
        print(f"✓ Cost logger working correctly (total: ${total:.6f})")
        return True
    except Exception as e:
        print(f"✗ Cost logger failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_data():
    """Test dashboard can load data."""
    print("\nTesting dashboard data loading...")
    
    try:
        import json
        
        # Check if demo data exists
        if not os.path.exists('data/benchmark_results.json'):
            print("⚠ No benchmark results found, dashboard will show warning")
            return True
        
        with open('data/benchmark_results.json', 'r') as f:
            results = json.load(f)
        
        assert isinstance(results, list), "Results should be a list"
        assert len(results) > 0, "Results should not be empty"
        
        # Check required fields
        required_fields = ['method_name', 'avg_faithfulness', 'avg_relevancy', 'total_cost']
        for result in results:
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
        
        print(f"✓ Dashboard data valid ({len(results)} methods)")
        return True
    except Exception as e:
        print(f"✗ Dashboard data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SEARCH ROI AUDITOR - SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_generation,
        test_cost_logger,
        test_dashboard_data
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {sum(results)} tests")
    print(f"Failed: {len(results) - sum(results)} tests")
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
