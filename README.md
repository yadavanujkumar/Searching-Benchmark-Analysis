# Search ROI Auditor 🔍

A comprehensive benchmarking system that analyzes search techniques by correlating accuracy metrics with real-world infrastructure costs. This tool helps you make data-driven decisions about which search method to use based on accuracy, cost, and performance requirements.

## 🎯 Features

### Core Capabilities

1. **Metric-Heavy Indexing**
   - Index datasets into Elasticsearch (Keyword search)
   - Index datasets into Qdrant (Vector search)
   - Track exact memory and storage footprint for each method

2. **Accuracy Evaluation**
   - Uses DeepEval to run comprehensive test queries
   - Generates Faithfulness and Relevancy scores for each query
   - Supports 100+ test queries out of the box

3. **Real-Time Cost Logging**
   - Calculates embedding API call costs (OpenAI)
   - Tracks vector DB compute time costs
   - Monitors lexical DB query latency costs
   - Provides detailed cost breakdowns

4. **Decision Matrix UI**
   - Interactive Streamlit dashboard
   - Leaderboard showing best "Accuracy-per-Dollar" methods
   - Intelligent Recommendation Engine for different use cases
   - Visual comparisons of accuracy, cost, and performance

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Elasticsearch 8.x (optional - can run without)
- Qdrant (optional - can run without)
- OpenAI API key (required for embeddings)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yadavanujkumar/Searching-Benchmark-Analysis.git
cd Searching-Benchmark-Analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Usage

#### Option 1: Quick Demo (Without External Services)

Run the benchmark with mock data:
```bash
python run_benchmark.py
```

#### Option 2: Full Benchmark (With Elasticsearch and Qdrant)

1. Start Elasticsearch:
```bash
docker run -d -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.12.0
```

2. Start Qdrant:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

3. Run benchmark:
```bash
python run_benchmark.py
```

#### View Results

Launch the interactive dashboard:
```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Dashboard Features

![Dashboard Preview](https://github.com/user-attachments/assets/de658239-cb8c-4cfc-8c92-2ccca0c4cc51)

The interactive dashboard provides comprehensive insights into search performance and costs:

### 1. Leaderboard
View which search method provides the best accuracy-per-dollar ratio:
- Elasticsearch (Keyword)
- Qdrant (Vector)
- Hybrid (Combined)

### 2. Cost Breakdown
Detailed visualization of:
- Embedding API costs
- Vector database query costs
- Lexical database query costs

### 3. Accuracy Comparison
Compare Faithfulness and Relevancy scores across methods

### 4. Recommendation Engine
Get smart recommendations for different use cases:
- **Technical part-number searches**: Use Keyword (99% accuracy, $0.001 cost)
- **Customer questions**: Use Hybrid (92% accuracy, $0.05 cost)
- **High-volume applications**: Best value method
- **Real-time systems**: Fastest response method

### 5. Resource Usage
View memory and storage footprints for each indexing method

## 🏗️ Architecture

```
├── src/
│   ├── indexing/
│   │   ├── elasticsearch_indexer.py  # Keyword search indexing
│   │   └── qdrant_indexer.py         # Vector search indexing
│   ├── evaluation/
│   │   └── accuracy_evaluator.py     # DeepEval integration
│   ├── cost_tracking/
│   │   └── cost_logger.py            # Cost calculation
│   └── dashboard/
│       └── app.py                    # Streamlit dashboard
├── data/
│   └── sample_data.py                # Sample dataset generator
├── run_benchmark.py                  # Main benchmark runner
└── requirements.txt                  # Dependencies
```

## 🔧 Configuration

Edit `.env` to customize:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_key_here

# Elasticsearch (optional)
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Qdrant (optional)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Cost Configuration (per 1000 tokens/embeddings)
EMBEDDING_COST_PER_1K=0.0001
VECTOR_DB_COST_PER_QUERY=0.00001
LEXICAL_DB_COST_PER_QUERY=0.000001
```

## 📈 Sample Results

Example output from benchmarking:

| Method | Faithfulness | Relevancy | Cost | Accuracy/$ |
|--------|-------------|-----------|------|------------|
| Keyword | 87.5% | 89.2% | $0.0012 | 73,916 |
| Vector | 92.3% | 94.1% | $0.0523 | 1,782 |
| Hybrid | 94.8% | 95.6% | $0.0535 | 1,782 |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [DeepEval](https://github.com/confident-ai/deepeval)
- Uses [Elasticsearch](https://www.elastic.co/) for keyword search
- Uses [Qdrant](https://qdrant.tech/) for vector search
- Dashboard powered by [Streamlit](https://streamlit.io/)

## 📞 Support

For issues and questions, please open an issue on GitHub.