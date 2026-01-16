# Search ROI Auditor - Usage Guide

## Quick Start Guide

### Option 1: Demo Mode (No External Dependencies)

The fastest way to see the system in action:

```bash
# 1. Install minimal dependencies
pip install streamlit pandas plotly

# 2. Generate demo data
python demo_mode.py

# 3. Launch dashboard
streamlit run src/dashboard/app.py
```

The dashboard will open at `http://localhost:8501` with sample data demonstrating the system's capabilities.

### Option 2: Full Benchmark with Docker

For a complete benchmarking experience:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here

# 3. Run the quick start script
./quick_start.sh
```

This script will:
- Install Python dependencies
- Start Elasticsearch and Qdrant via Docker Compose
- Run the full benchmark
- Launch the dashboard

### Option 3: Manual Setup

For complete control:

```bash
# 1. Install all dependencies
pip install -r requirements.txt

# 2. Start search engines
docker-compose up -d

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run benchmark
python run_benchmark.py

# 5. View results
streamlit run src/dashboard/app.py
```

## Detailed Usage

### Running Benchmarks

#### Basic Benchmark

```bash
python run_benchmark.py
```

This runs a standard benchmark with:
- 100 documents indexed
- 100 test queries executed
- 3 search methods tested (Keyword, Vector, Hybrid)

#### Custom Dataset Size

Edit `run_benchmark.py` and modify the main function:

```python
def main():
    runner = BenchmarkRunner()
    runner.run(num_documents=500, num_queries=200)
```

#### Using Your Own Data

Replace the sample data generator with your own data:

```python
# In run_benchmark.py
from your_module import load_your_data

def main():
    runner = BenchmarkRunner()
    
    # Load your data
    documents = load_your_data()
    test_queries = load_your_queries()
    
    # Run benchmark
    runner.setup_indexers()
    runner.index_data(documents)
    # ... continue with evaluation
```

### Dashboard Features

#### 1. Leaderboard

Shows ranking of search methods by Accuracy-per-Dollar.

**How to interpret:**
- Higher score = better value
- Look at both accuracy percentages and costs
- Consider your specific use case requirements

**Example interpretation:**
```
Method: Elasticsearch (Keyword)
Accuracy/Dollar: 73,916
→ Best for high-volume, cost-sensitive applications

Method: Hybrid (Keyword + Vector)
Accuracy/Dollar: 1,782
→ Best when accuracy is paramount
```

#### 2. Cost Breakdown

Visualizes where your money goes for each search method.

**Cost components:**
- **Embedding Cost**: OpenAI API calls for vector generation
- **Vector Query Cost**: Qdrant search operations
- **Lexical Query Cost**: Elasticsearch search operations

**Optimization tips:**
- Cache embeddings to reduce API costs
- Use keyword search for exact matches
- Reserve vector search for semantic queries

#### 3. Accuracy Comparison

Compare Faithfulness and Relevancy scores across methods.

**Metric definitions:**
- **Faithfulness**: Are results factually accurate?
- **Relevancy**: Are results pertinent to the query?

**Target scores:**
- 90%+ = Excellent
- 80-90% = Good
- 70-80% = Acceptable
- <70% = Needs improvement

#### 4. Recommendation Engine

Provides use-case specific guidance.

**Recommendations include:**
- **Highest Accuracy**: For critical applications
- **Best Value**: For cost-sensitive scenarios
- **Fastest Response**: For real-time systems
- **Technical Searches**: For exact matches (part numbers)
- **Natural Language**: For customer queries

### Configuration

#### Cost Configuration

Edit `.env` to match your infrastructure costs:

```env
# OpenAI Embeddings (text-embedding-ada-002)
EMBEDDING_COST_PER_1K=0.0001

# Adjust based on your cloud provider
VECTOR_DB_COST_PER_QUERY=0.00001
LEXICAL_DB_COST_PER_QUERY=0.000001
```

**Finding your costs:**
- OpenAI: Check [pricing page](https://openai.com/pricing)
- Qdrant: Calculate from instance costs
- Elasticsearch: Calculate from instance or Elastic Cloud costs

#### Search Engine Configuration

```env
# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

For cloud deployments, update with your endpoints:
```env
ELASTICSEARCH_HOST=your-cluster.es.cloud
QDRANT_HOST=your-cluster.qdrant.cloud
```

### Advanced Usage

#### Selective Benchmarking

Run only specific search methods by commenting out others in `run_benchmark.py`:

```python
def run(self):
    # ... setup code ...
    
    self.run_keyword_search_benchmark(test_queries)
    # self.run_vector_search_benchmark(test_queries)  # Skip this
    # self.run_hybrid_search_benchmark(test_queries)  # Skip this
```

#### Custom Test Queries

Create domain-specific test queries in `data/sample_data.py`:

```python
def generate_test_queries(count: int = 100):
    queries = []
    
    # Your custom queries
    queries.append({
        "query": "Your specific query",
        "type": "semantic",
        "expected": "Expected result description"
    })
    
    return queries
```

#### Export Results

Results are saved as JSON and can be exported:

```python
import json
import pandas as pd

# Load results
with open('data/benchmark_results.json', 'r') as f:
    results = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(results)

# Export to CSV
df.to_csv('benchmark_results.csv', index=False)

# Export to Excel
df.to_excel('benchmark_results.xlsx', index=False)
```

#### Continuous Monitoring

Set up cron job for regular benchmarks:

```bash
# Run benchmark daily at 2 AM
0 2 * * * cd /path/to/project && python run_benchmark.py >> logs/benchmark.log 2>&1
```

### Interpreting Results

#### Example Scenario 1: E-commerce Product Search

**Requirements:**
- 10,000 products
- 1M queries/month
- Mix of exact (SKU) and fuzzy (description) searches

**Benchmark Results:**
```
Keyword:  88% accuracy, $12/month
Vector:   94% accuracy, $5,200/month
Hybrid:   96% accuracy, $5,212/month
```

**Decision:** Use Hybrid for main search, Keyword for SKU-specific searches
**Savings:** Implement smart routing → $2,000/month

#### Example Scenario 2: Technical Documentation Search

**Requirements:**
- 5,000 documents
- 100K queries/month
- Mostly exact term searches

**Benchmark Results:**
```
Keyword:  91% accuracy, $1.20/month
Vector:   89% accuracy, $520/month
Hybrid:   92% accuracy, $521/month
```

**Decision:** Use Keyword search exclusively
**Savings:** $519/month vs Vector

#### Example Scenario 3: Customer Support Bot

**Requirements:**
- 2,000 FAQ entries
- 500K queries/month (varied natural language)

**Benchmark Results:**
```
Keyword:  75% accuracy, $6/month
Vector:   95% accuracy, $2,600/month
Hybrid:   97% accuracy, $2,606/month
```

**Decision:** Use Hybrid for quality customer experience
**ROI:** Higher satisfaction justifies cost

### Best Practices

#### 1. Start Small
- Test with 100 documents and 50 queries first
- Verify setup and configuration
- Scale up gradually

#### 2. Use Representative Data
- Use actual or similar data from your use case
- Include edge cases and variations
- Cover different query types

#### 3. Monitor Costs
- Set up billing alerts
- Track API usage
- Review costs after each run

#### 4. Iterate and Optimize
- Run benchmarks after configuration changes
- A/B test different approaches
- Document findings

#### 5. Regular Benchmarking
- Re-run quarterly or after major changes
- Track performance trends
- Update cost models as prices change

### Troubleshooting

#### Problem: High API Costs

**Solutions:**
- Reduce dataset size for testing
- Cache embeddings
- Use smaller embedding models
- Implement query sampling

#### Problem: Low Accuracy Scores

**Possible causes:**
- Inappropriate search method for query type
- Poor quality test queries
- Insufficient indexed data
- DeepEval model mismatch

**Solutions:**
- Review test query design
- Ensure adequate training data
- Try different search configurations
- Adjust DeepEval thresholds

#### Problem: Slow Benchmarks

**Optimizations:**
- Reduce query count
- Use batch processing
- Enable parallel execution
- Optimize network latency

#### Problem: Inconsistent Results

**Causes:**
- Non-deterministic LLM evaluations
- Network variability
- Resource contention

**Solutions:**
- Run multiple iterations
- Use averaged results
- Control for external factors
- Seed random operations

### Support and Resources

**Documentation:**
- README.md - Quick overview
- ARCHITECTURE.md - System design
- This file - Detailed usage

**Examples:**
- demo_mode.py - Mock data demo
- test_system.py - Component testing
- run_benchmark.py - Full example

**Getting Help:**
- Check troubleshooting section
- Review error messages carefully
- Open GitHub issues for bugs
- Check dependencies and versions

## Next Steps

1. Run demo mode to familiarize yourself with the dashboard
2. Set up real search engines for accurate benchmarking
3. Customize test queries for your domain
4. Run full benchmark and analyze results
5. Make data-driven decisions about search technology
6. Monitor and iterate based on real-world usage

Happy benchmarking! 🚀
