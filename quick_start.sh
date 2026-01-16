#!/bin/bash

# Search ROI Auditor - Quick Start Script

echo "========================================"
echo "Search ROI Auditor - Quick Start"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  OpenAI API key not configured in .env"
    echo "   Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

echo "1. Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "2. Starting services with Docker Compose..."
docker-compose up -d
echo "✓ Services started"
echo ""

echo "3. Waiting for services to be ready..."
echo "   - Elasticsearch..."
sleep 10
until curl -s http://localhost:9200 > /dev/null; do
    echo "   Waiting for Elasticsearch..."
    sleep 2
done
echo "   ✓ Elasticsearch ready"

echo "   - Qdrant..."
until curl -s http://localhost:6333/health > /dev/null; do
    echo "   Waiting for Qdrant..."
    sleep 2
done
echo "   ✓ Qdrant ready"
echo ""

echo "4. Running benchmark..."
python run_benchmark.py
echo ""

echo "5. Starting dashboard..."
echo ""
echo "========================================"
echo "Dashboard will open at:"
echo "http://localhost:8501"
echo "========================================"
echo ""
streamlit run src/dashboard/app.py
