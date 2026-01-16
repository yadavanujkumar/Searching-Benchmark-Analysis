"""
Search ROI Auditor - Streamlit Dashboard
Decision Matrix UI with Leaderboard and Recommendation Engine
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import json
import os


class SearchROIDashboard:
    """Dashboard for visualizing search ROI analysis."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Search ROI Auditor",
            page_icon="🔍",
            layout="wide"
        )
        
    def render_header(self):
        """Render dashboard header."""
        st.title("🔍 Search ROI Auditor")
        st.markdown("### Benchmarking Search Techniques: Accuracy vs. Infrastructure Costs")
        st.markdown("---")
    
    def render_leaderboard(self, results: List[Dict[str, Any]]):
        """
        Render the leaderboard showing Accuracy-per-Dollar.
        
        Args:
            results: List of benchmark results for different search methods
        """
        st.header("📊 Leaderboard: Best Accuracy-per-Dollar")
        
        if not results:
            st.warning("No results available. Please run benchmarks first.")
            return
        
        # Calculate accuracy-per-dollar metric
        leaderboard_data = []
        for result in results:
            method = result["method_name"]
            avg_accuracy = (result.get("avg_faithfulness", 0) + result.get("avg_relevancy", 0)) / 2
            total_cost = result.get("total_cost", 0.001)  # Avoid division by zero
            accuracy_per_dollar = avg_accuracy / total_cost if total_cost > 0 else 0
            
            leaderboard_data.append({
                "Method": method,
                "Avg Faithfulness": f"{result.get('avg_faithfulness', 0):.2%}",
                "Avg Relevancy": f"{result.get('avg_relevancy', 0):.2%}",
                "Total Cost": f"${total_cost:.4f}",
                "Accuracy/Dollar": f"{accuracy_per_dollar:.2f}",
                "Query Count": result.get("num_queries", 0),
                "Avg Search Time": f"{result.get('avg_search_time', 0):.3f}s"
            })
        
        # Sort by Accuracy-per-Dollar
        df = pd.DataFrame(leaderboard_data)
        df["sort_key"] = df["Accuracy/Dollar"].str.replace(",", "").astype(float)
        df = df.sort_values("sort_key", ascending=False).drop("sort_key", axis=1)
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visualize with bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=df["Method"],
                y=[float(x) for x in df["Accuracy/Dollar"]],
                marker_color='rgb(55, 83, 109)',
                text=[float(x) for x in df["Accuracy/Dollar"]],
                texttemplate='%{text:.1f}',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Accuracy per Dollar Comparison",
            xaxis_title="Search Method",
            yaxis_title="Accuracy per Dollar",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_cost_breakdown(self, results: List[Dict[str, Any]]):
        """
        Render cost breakdown visualization.
        
        Args:
            results: List of benchmark results
        """
        st.header("💰 Cost Breakdown")
        
        if not results:
            return
        
        # Prepare data for visualization
        cost_data = []
        for result in results:
            method = result["method_name"]
            breakdown = result.get("cost_breakdown", {})
            
            cost_data.append({
                "Method": method,
                "Embedding": breakdown.get("embedding_cost", 0),
                "Vector Query": breakdown.get("vector_query_cost", 0),
                "Lexical Query": breakdown.get("lexical_query_cost", 0)
            })
        
        df = pd.DataFrame(cost_data)
        
        # Stacked bar chart
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        for i, col in enumerate(['Embedding', 'Vector Query', 'Lexical Query']):
            fig.add_trace(go.Bar(
                name=col,
                x=df['Method'],
                y=df[col],
                marker_color=colors[i]
            ))
        
        fig.update_layout(
            barmode='stack',
            title='Cost Breakdown by Method',
            xaxis_title='Search Method',
            yaxis_title='Cost ($)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_accuracy_comparison(self, results: List[Dict[str, Any]]):
        """
        Render accuracy comparison chart.
        
        Args:
            results: List of benchmark results
        """
        st.header("🎯 Accuracy Comparison")
        
        if not results:
            return
        
        # Prepare data
        methods = []
        faithfulness = []
        relevancy = []
        
        for result in results:
            methods.append(result["method_name"])
            faithfulness.append(result.get("avg_faithfulness", 0) * 100)
            relevancy.append(result.get("avg_relevancy", 0) * 100)
        
        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(name='Faithfulness', x=methods, y=faithfulness, marker_color='#4A90E2'),
            go.Bar(name='Relevancy', x=methods, y=relevancy, marker_color='#F39C12')
        ])
        
        fig.update_layout(
            barmode='group',
            title='Accuracy Metrics by Method',
            xaxis_title='Search Method',
            yaxis_title='Score (%)',
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_recommendation_engine(self, results: List[Dict[str, Any]]):
        """
        Render recommendation engine with smart suggestions.
        
        Args:
            results: List of benchmark results
        """
        st.header("🤖 Recommendation Engine")
        
        if not results:
            st.info("Run benchmarks to get recommendations.")
            return
        
        # Analyze results and generate recommendations
        recommendations = self._generate_recommendations(results)
        
        # Display recommendations in cards
        for rec in recommendations:
            with st.container():
                st.markdown(f"### {rec['use_case']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Recommended Method:** `{rec['method']}`")
                    st.markdown(f"_{rec['reason']}_")
                
                with col2:
                    st.metric("Accuracy", f"{rec['accuracy']:.1%}")
                
                with col3:
                    st.metric("Cost", f"${rec['cost']:.4f}")
                
                st.markdown("---")
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate smart recommendations based on benchmark results.
        
        Args:
            results: Benchmark results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Find best method for different use cases
        
        # 1. Best accuracy regardless of cost
        best_accuracy = max(results, key=lambda x: (x.get("avg_faithfulness", 0) + x.get("avg_relevancy", 0)) / 2)
        avg_acc = (best_accuracy.get("avg_faithfulness", 0) + best_accuracy.get("avg_relevancy", 0)) / 2
        recommendations.append({
            "use_case": "🎯 Highest Accuracy (Critical Applications)",
            "method": best_accuracy["method_name"],
            "reason": "This method provides the highest accuracy scores, ideal for applications where precision is paramount.",
            "accuracy": avg_acc,
            "cost": best_accuracy.get("total_cost", 0)
        })
        
        # 2. Best cost efficiency
        for result in results:
            result["_efficiency"] = (result.get("avg_faithfulness", 0) + result.get("avg_relevancy", 0)) / (2 * max(result.get("total_cost", 0.001), 0.001))
        
        best_efficiency = max(results, key=lambda x: x["_efficiency"])
        avg_eff_acc = (best_efficiency.get("avg_faithfulness", 0) + best_efficiency.get("avg_relevancy", 0)) / 2
        recommendations.append({
            "use_case": "💰 Best Value (High Volume Applications)",
            "method": best_efficiency["method_name"],
            "reason": "This method offers the best accuracy-per-dollar ratio, perfect for high-volume queries where cost matters.",
            "accuracy": avg_eff_acc,
            "cost": best_efficiency.get("total_cost", 0)
        })
        
        # 3. Fastest response time
        fastest = min(results, key=lambda x: x.get("avg_search_time", float('inf')))
        avg_fast_acc = (fastest.get("avg_faithfulness", 0) + fastest.get("avg_relevancy", 0)) / 2
        recommendations.append({
            "use_case": "⚡ Fastest Response (Real-Time Systems)",
            "method": fastest["method_name"],
            "reason": f"This method has the lowest latency ({fastest.get('avg_search_time', 0):.3f}s), ideal for real-time applications.",
            "accuracy": avg_fast_acc,
            "cost": fastest.get("total_cost", 0)
        })
        
        # 4. Specific use case recommendations
        keyword_methods = [r for r in results if "keyword" in r["method_name"].lower() or "elasticsearch" in r["method_name"].lower()]
        if keyword_methods:
            best_keyword = max(keyword_methods, key=lambda x: (x.get("avg_faithfulness", 0) + x.get("avg_relevancy", 0)) / 2)
            avg_kw_acc = (best_keyword.get("avg_faithfulness", 0) + best_keyword.get("avg_relevancy", 0)) / 2
            recommendations.append({
                "use_case": "🔤 Technical Part-Number Searches",
                "method": best_keyword["method_name"],
                "reason": "Keyword search excels at exact matches for technical queries, part numbers, and structured data.",
                "accuracy": avg_kw_acc,
                "cost": best_keyword.get("total_cost", 0)
            })
        
        vector_methods = [r for r in results if "vector" in r["method_name"].lower() or "qdrant" in r["method_name"].lower()]
        if vector_methods:
            best_vector = max(vector_methods, key=lambda x: (x.get("avg_faithfulness", 0) + x.get("avg_relevancy", 0)) / 2)
            avg_vec_acc = (best_vector.get("avg_faithfulness", 0) + best_vector.get("avg_relevancy", 0)) / 2
            recommendations.append({
                "use_case": "💬 Natural Language Customer Questions",
                "method": best_vector["method_name"],
                "reason": "Vector search understands semantic meaning, perfect for conversational queries and customer support.",
                "accuracy": avg_vec_acc,
                "cost": best_vector.get("total_cost", 0)
            })
        
        return recommendations
    
    def render_resource_usage(self, indexing_results: Dict[str, Any]):
        """
        Render resource usage metrics from indexing.
        
        Args:
            indexing_results: Results from indexing operations
        """
        st.header("💾 Resource Usage")
        
        if not indexing_results:
            return
        
        col1, col2 = st.columns(2)
        
        for method, stats in indexing_results.items():
            with col1 if "elasticsearch" in method.lower() else col2:
                st.subheader(method)
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.metric("Memory Usage", f"{stats.get('memory_usage_mb', 0):.2f} MB")
                    st.metric("Duration", f"{stats.get('duration_seconds', 0):.2f}s")
                
                with metrics_col2:
                    st.metric("Storage", f"{stats.get('storage_usage_mb', 0):.2f} MB")
                    st.metric("Documents", stats.get('documents_indexed', 0))


def main():
    """Main dashboard entry point."""
    dashboard = SearchROIDashboard()
    dashboard.render_header()
    
    # Load results if available
    results_file = "data/benchmark_results.json"
    indexing_file = "data/indexing_results.json"
    
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Render all sections
        dashboard.render_leaderboard(results)
        
        col1, col2 = st.columns(2)
        with col1:
            dashboard.render_accuracy_comparison(results)
        with col2:
            dashboard.render_cost_breakdown(results)
        
        dashboard.render_recommendation_engine(results)
        
        # Load and render indexing results
        if os.path.exists(indexing_file):
            with open(indexing_file, 'r') as f:
                indexing_results = json.load(f)
            dashboard.render_resource_usage(indexing_results)
    else:
        st.warning("⚠️ No benchmark results found. Please run the benchmarking script first.")
        st.info("Run: `python run_benchmark.py` to generate results.")


if __name__ == "__main__":
    main()
