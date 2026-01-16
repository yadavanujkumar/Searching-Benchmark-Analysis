"""
Accuracy evaluation module using DeepEval.
"""
import time
from typing import List, Dict, Any
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


class AccuracyEvaluator:
    """Evaluates search accuracy using DeepEval metrics."""
    
    def __init__(self):
        self.faithfulness_metric = FaithfulnessMetric(threshold=0.7, model="gpt-3.5-turbo")
        self.relevancy_metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-3.5-turbo")
        
    def evaluate_query(
        self, 
        query: str, 
        retrieved_contexts: List[str],
        expected_output: str = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single query using Faithfulness and Relevancy metrics.
        
        Args:
            query: The search query
            retrieved_contexts: List of retrieved document contents
            expected_output: Expected answer (optional, can be generated)
            
        Returns:
            Dictionary with evaluation scores
        """
        # If no expected output, use the first retrieved context
        if expected_output is None and retrieved_contexts:
            expected_output = retrieved_contexts[0]
        elif expected_output is None:
            expected_output = "No relevant information found."
        
        # Create test case
        test_case = LLMTestCase(
            input=query,
            actual_output=expected_output,
            retrieval_context=retrieved_contexts
        )
        
        start_time = time.time()
        
        # Evaluate faithfulness
        try:
            self.faithfulness_metric.measure(test_case)
            faithfulness_score = self.faithfulness_metric.score
        except Exception as e:
            print(f"Faithfulness evaluation error: {e}")
            faithfulness_score = 0.0
        
        # Evaluate relevancy
        try:
            self.relevancy_metric.measure(test_case)
            relevancy_score = self.relevancy_metric.score
        except Exception as e:
            print(f"Relevancy evaluation error: {e}")
            relevancy_score = 0.0
        
        evaluation_time = time.time() - start_time
        
        return {
            "query": query,
            "faithfulness_score": faithfulness_score,
            "relevancy_score": relevancy_score,
            "evaluation_time": evaluation_time,
            "num_contexts": len(retrieved_contexts)
        }
    
    def evaluate_search_method(
        self,
        test_queries: List[Dict[str, str]],
        search_function,
        method_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate a search method on multiple test queries.
        
        Args:
            test_queries: List of test query dictionaries with 'query' and optional 'expected'
            search_function: Function that takes a query and returns results
            method_name: Name of the search method
            
        Returns:
            Aggregated evaluation results
        """
        results = []
        total_time = 0
        
        for i, test_query in enumerate(test_queries):
            query = test_query.get("query", "")
            expected = test_query.get("expected", None)
            
            print(f"Evaluating query {i+1}/{len(test_queries)}: {query[:50]}...")
            
            # Get search results
            search_start = time.time()
            search_results = search_function(query)
            search_time = time.time() - search_start
            
            # Extract contexts from search results
            contexts = []
            for result in search_results[:5]:  # Top 5 results
                if isinstance(result, dict):
                    content = result.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("content", content.get("title", ""))
                    else:
                        text = str(content)
                    contexts.append(text)
            
            # Evaluate
            eval_result = self.evaluate_query(query, contexts, expected)
            eval_result["search_time"] = search_time
            results.append(eval_result)
            
            total_time += search_time + eval_result["evaluation_time"]
        
        # Calculate aggregated metrics
        avg_faithfulness = sum(r["faithfulness_score"] for r in results) / len(results) if results else 0
        avg_relevancy = sum(r["relevancy_score"] for r in results) / len(results) if results else 0
        avg_search_time = sum(r["search_time"] for r in results) / len(results) if results else 0
        
        return {
            "method_name": method_name,
            "num_queries": len(test_queries),
            "avg_faithfulness": avg_faithfulness,
            "avg_relevancy": avg_relevancy,
            "avg_search_time": avg_search_time,
            "total_time": total_time,
            "detailed_results": results
        }
