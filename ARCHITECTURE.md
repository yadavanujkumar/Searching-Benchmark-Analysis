# Search ROI Auditor - Architecture

## Overview

The Search ROI Auditor is a comprehensive benchmarking system designed to help organizations make data-driven decisions about search technology investments. It evaluates different search methodologies by measuring both their accuracy and infrastructure costs, providing actionable insights through an interactive dashboard.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Search ROI Auditor                           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Indexing   │      │  Evaluation  │     │     Cost     │
│    Module    │      │    Module    │     │   Tracking   │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────────────────────────────────────────────────┐
│                    Benchmark Runner                       │
│                 (Orchestration Layer)                     │
└──────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Data Storage   │
                    │  (JSON Results)  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Dashboard     │
                    │   (Streamlit)    │
                    └──────────────────┘
```

## Core Components

### 1. Indexing Module (`src/indexing/`)

Handles data ingestion into different search engines with comprehensive resource tracking.

#### ElasticsearchIndexer
- **Purpose**: Indexes documents using keyword-based search
- **Features**:
  - Full-text search with BM25 ranking
  - Multi-field matching (title^2, content)
  - Memory and storage footprint tracking
  - Bulk indexing support
- **Metrics Tracked**:
  - Memory usage (MB)
  - Storage usage (MB)
  - Indexing duration
  - Document count

#### QdrantIndexer
- **Purpose**: Indexes documents as vectors for semantic search
- **Features**:
  - OpenAI embedding generation
  - Cosine similarity search
  - Vector storage with payload
  - Batch processing
- **Metrics Tracked**:
  - Embedding API calls
  - Memory usage (MB)
  - Storage usage (MB)
  - Indexing duration

### 2. Evaluation Module (`src/evaluation/`)

Uses DeepEval framework to assess search quality.

#### AccuracyEvaluator
- **Metrics**:
  - **Faithfulness**: Measures if retrieved information is factually consistent
  - **Relevancy**: Measures how relevant results are to the query
- **Process**:
  1. Execute search query
  2. Extract top N results as context
  3. Evaluate using LLM-based metrics
  4. Aggregate scores across multiple queries
- **Output**: Per-query and aggregated accuracy scores

### 3. Cost Tracking Module (`src/cost_tracking/`)

Real-time cost calculation for all operations.

#### CostLogger
Tracks costs for:
- **Embedding API Calls**: $0.0001 per 1K tokens (configurable)
- **Vector DB Queries**: Base cost + compute time
- **Lexical DB Queries**: Base cost + latency

#### HybridSearchCostTracker
Specialized tracker for comparing multiple search methods in a single benchmark run.

### 4. Dashboard (`src/dashboard/`)

Interactive Streamlit application for visualization and decision-making.

#### Key Features:

**Leaderboard**
- Ranks methods by Accuracy-per-Dollar
- Shows comprehensive metrics table
- Visual bar chart comparison

**Cost Breakdown**
- Stacked bar chart showing cost components
- Embedding, vector query, and lexical query costs
- Per-method breakdown

**Accuracy Comparison**
- Grouped bar chart for Faithfulness vs Relevancy
- Side-by-side method comparison
- Percentage-based scoring

**Recommendation Engine**
- Context-aware suggestions
- Use-case specific recommendations:
  - Technical part-number searches → Keyword
  - Natural language questions → Vector/Hybrid
  - High-volume applications → Best value method
  - Real-time systems → Fastest method

**Resource Usage**
- Memory and storage metrics
- Indexing performance stats
- Visual comparison across methods

## Data Flow

### Benchmarking Process

1. **Initialization**
   ```
   User runs: python run_benchmark.py
   ```

2. **Data Generation**
   ```
   generate_sample_dataset(100) → Documents
   generate_test_queries(100) → Test Queries
   ```

3. **Indexing Phase**
   ```
   For each search engine:
     - Connect to engine
     - Create index/collection
     - Index documents
     - Track resource usage
     - Save metrics
   ```

4. **Evaluation Phase**
   ```
   For each search method:
     For each test query:
       - Execute search
       - Track latency and cost
       - Evaluate accuracy (Faithfulness + Relevancy)
       - Store results
     
     Aggregate results:
       - Average accuracy scores
       - Total costs
       - Performance metrics
   ```

5. **Results Storage**
   ```
   Save to JSON:
     - data/benchmark_results.json
     - data/indexing_results.json
   ```

6. **Visualization**
   ```
   User runs: streamlit run src/dashboard/app.py
   Dashboard loads and displays results
   ```

## Search Methods Compared

### 1. Keyword Search (Elasticsearch)
- **Best For**: Exact matches, technical queries, part numbers
- **Pros**: Fast, low cost, deterministic
- **Cons**: Limited semantic understanding
- **Typical Cost**: $0.001 per 100 queries

### 2. Vector Search (Qdrant)
- **Best For**: Natural language, semantic similarity, fuzzy matching
- **Pros**: Understands intent, handles variations
- **Cons**: Higher cost, requires embeddings
- **Typical Cost**: $0.05 per 100 queries

### 3. Hybrid Search (Keyword + Vector)
- **Best For**: Complex queries requiring both precision and recall
- **Pros**: Best accuracy, combines strengths
- **Cons**: Highest cost, more complex
- **Typical Cost**: $0.054 per 100 queries

## Configuration

### Environment Variables (.env)

```env
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults provided)
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Cost Configuration
EMBEDDING_COST_PER_1K=0.0001
VECTOR_DB_COST_PER_QUERY=0.00001
LEXICAL_DB_COST_PER_QUERY=0.000001
```

### Customization

All configuration can be customized through:
- Environment variables
- `config/config.py` module
- Command-line parameters (future enhancement)

## Extensibility

### Adding New Search Methods

1. Create a new indexer in `src/indexing/`
2. Implement:
   - `connect()`: Establish connection
   - `create_index()`: Set up data structure
   - `index_documents()`: Load data
   - `search()`: Execute queries
3. Add to benchmark runner
4. Run benchmarks and view in dashboard

### Adding New Metrics

1. Extend `AccuracyEvaluator` in `src/evaluation/`
2. Add new DeepEval metrics or custom metrics
3. Update dashboard to display new metrics
4. Modify recommendation engine logic as needed

### Custom Cost Models

1. Update `CostLogger` in `src/cost_tracking/`
2. Add new cost calculation methods
3. Update environment variables
4. Modify dashboard cost breakdown

## Performance Considerations

### Scalability
- **Documents**: Tested with 100-10,000 documents
- **Queries**: Supports 100-1,000+ test queries
- **Concurrent Operations**: Batch processing for efficiency

### Resource Requirements
- **Memory**: ~500MB base + data dependent
- **Storage**: ~100MB for sample data
- **Network**: API calls for embeddings (can be cached)

### Optimization Strategies
1. **Batch Processing**: Index and embed in batches
2. **Caching**: Cache embeddings for repeated queries
3. **Sampling**: Test on subset before full benchmark
4. **Parallel Execution**: Run independent benchmarks in parallel

## Security Considerations

### API Keys
- Store in `.env` file (gitignored)
- Never commit to version control
- Use environment-specific keys

### Data Privacy
- Sample data is synthetic
- Real data should be anonymized
- Dashboard runs locally by default

### Cost Controls
- Set API rate limits
- Monitor costs during runs
- Use budget alerts
- Test with small datasets first

## Future Enhancements

### Planned Features
1. **Real-time Monitoring**: Live cost tracking during benchmarks
2. **Historical Comparison**: Track performance over time
3. **A/B Testing**: Compare configuration changes
4. **Export Reports**: PDF/CSV report generation
5. **Cloud Deployment**: Hosted dashboard option
6. **More Search Engines**: Solr, Typesense, Meilisearch support
7. **Custom Datasets**: Upload your own data for benchmarking
8. **Multi-Language**: Support for non-English content

### Integration Opportunities
- CI/CD pipelines for regression testing
- Slack/Email notifications for benchmark completion
- Integration with existing monitoring tools
- API for programmatic access

## Troubleshooting

### Common Issues

**Issue**: Elasticsearch connection failed
- **Solution**: Ensure Elasticsearch is running on correct port
- **Alternative**: Run demo mode without external dependencies

**Issue**: OpenAI API errors
- **Solution**: Check API key, rate limits, and quotas
- **Alternative**: Use cached embeddings or demo mode

**Issue**: Out of memory during indexing
- **Solution**: Reduce batch size or dataset size
- **Tip**: Monitor memory usage during runs

**Issue**: Dashboard not showing results
- **Solution**: Ensure benchmark has been run first
- **Check**: data/benchmark_results.json exists

## References

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
