"""
Sample dataset generator for benchmarking.
"""
from typing import List, Dict, Any


def generate_sample_dataset(size: int = 100) -> List[Dict[str, Any]]:
    """
    Generate a sample dataset for indexing and testing.
    
    Args:
        size: Number of documents to generate
        
    Returns:
        List of documents
    """
    documents = []
    
    categories = [
        "Technical Documentation",
        "Product Specifications",
        "Customer Support",
        "Knowledge Base",
        "API Documentation"
    ]
    
    # Technical products and components
    products = [
        ("Widget-A-2000", "High-performance widget with advanced features"),
        ("Component-B-X100", "Industrial-grade component for heavy-duty applications"),
        ("Module-C-Pro", "Modular system with extensible architecture"),
        ("Sensor-D-Ultra", "High-precision sensor with real-time monitoring"),
        ("Controller-E-Max", "Intelligent controller with AI capabilities"),
    ]
    
    # Generate documents
    for i in range(size):
        product, desc = products[i % len(products)]
        category = categories[i % len(categories)]
        
        doc = {
            "id": f"DOC-{i+1:04d}",
            "title": f"{product} - {category}",
            "content": f"""
{product} Overview:

{desc}

Part Number: {product}
Category: {category}
SKU: SKU-{i+1:06d}

Technical Specifications:
- Operating Temperature: -40°C to 85°C
- Power Consumption: {5 + (i % 20)}W
- Dimensions: {10 + (i % 50)}mm x {20 + (i % 30)}mm x {5 + (i % 15)}mm
- Weight: {100 + (i % 500)}g
- Warranty: {1 + (i % 5)} years

Features:
- Advanced signal processing
- Low power consumption
- High reliability and durability
- Easy installation and maintenance
- Compatible with industry standards

Applications:
This product is suitable for industrial automation, manufacturing processes, 
quality control systems, and monitoring applications. It provides reliable 
performance in demanding environments and integrates seamlessly with existing 
infrastructure.

Documentation:
For detailed technical specifications, please refer to the complete documentation.
Installation guides and troubleshooting tips are available in the knowledge base.
For customer support, contact our technical team.
            """.strip(),
            "category": category,
            "metadata": {
                "sku": f"SKU-{i+1:06d}",
                "part_number": product,
                "price": 100 + (i * 10),
                "in_stock": i % 3 != 0
            }
        }
        
        documents.append(doc)
    
    return documents


def generate_test_queries(count: int = 100) -> List[Dict[str, str]]:
    """
    Generate test queries for evaluation.
    
    Args:
        count: Number of test queries to generate
        
    Returns:
        List of test query dictionaries
    """
    queries = []
    
    # Exact part number searches (technical)
    part_numbers = [
        "Widget-A-2000",
        "Component-B-X100",
        "Module-C-Pro",
        "Sensor-D-Ultra",
        "Controller-E-Max"
    ]
    
    for i, part in enumerate(part_numbers):
        queries.append({
            "query": f"Find {part}",
            "type": "exact_match",
            "expected": f"Technical information about {part}"
        })
        
        queries.append({
            "query": f"What is {part}?",
            "type": "semantic",
            "expected": f"Product overview and specifications for {part}"
        })
    
    # SKU searches
    for i in range(10):
        sku_num = (i * 10) + 1
        queries.append({
            "query": f"SKU-{sku_num:06d}",
            "type": "exact_match",
            "expected": f"Product with SKU-{sku_num:06d}"
        })
    
    # Natural language questions (semantic)
    nl_questions = [
        ("How do I install the widget?", "Installation instructions and setup guide"),
        ("What are the power requirements?", "Power consumption specifications"),
        ("Temperature specifications?", "Operating temperature range"),
        ("What is the warranty period?", "Warranty information"),
        ("Which products are suitable for industrial use?", "Industrial-grade products"),
        ("How to troubleshoot connection issues?", "Troubleshooting guide"),
        ("What are the dimensions?", "Physical dimensions and size"),
        ("Compatible products?", "Compatibility information"),
        ("How much does it weigh?", "Weight specifications"),
        ("What features are available?", "Product features and capabilities"),
    ]
    
    for question, expected in nl_questions:
        queries.append({
            "query": question,
            "type": "semantic",
            "expected": expected
        })
    
    # Technical specification searches
    tech_queries = [
        ("high temperature operation", "Products with high temperature range"),
        ("low power consumption", "Energy-efficient products"),
        ("compact size", "Small form factor products"),
        ("heavy duty applications", "Industrial-grade components"),
        ("real-time monitoring", "Products with monitoring capabilities"),
    ]
    
    for query, expected in tech_queries:
        queries.append({
            "query": query,
            "type": "semantic",
            "expected": expected
        })
    
    # Category-based searches
    categories = [
        "Technical Documentation",
        "Product Specifications",
        "Customer Support",
        "Knowledge Base",
        "API Documentation"
    ]
    
    for category in categories:
        queries.append({
            "query": f"Show me all {category}",
            "type": "category",
            "expected": f"Documents in {category} category"
        })
    
    # Mixed queries
    mixed_queries = [
        ("widget specifications and features", "Widget product specifications"),
        ("component installation guide", "Installation documentation for components"),
        ("sensor technical documentation", "Technical docs for sensors"),
        ("controller API reference", "API documentation for controllers"),
        ("module troubleshooting", "Troubleshooting guides for modules"),
    ]
    
    for query, expected in mixed_queries:
        queries.append({
            "query": query,
            "type": "mixed",
            "expected": expected
        })
    
    # Pad to requested count
    while len(queries) < count:
        queries.append({
            "query": f"General query about product {len(queries)}",
            "type": "general",
            "expected": "General product information"
        })
    
    return queries[:count]
