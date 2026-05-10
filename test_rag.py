#!/usr/bin/env python3
"""
Test script for RAG functionality.
This script tests the data ingestion and RAG query capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gateway'))

from gateway.services.data_ingestion import DataIngestionService
from gateway.services.llm_client import LLMClient
from gateway.config import settings


def test_data_ingestion():
    """Test data ingestion with PHI redaction."""
    print("Testing data ingestion...")

    data_service = DataIngestionService()

    # Clear existing data
    data_service.clear_collection()

    # Ingest synthetic data
    data_path = "data/synthetic_patients.json"
    if os.path.exists(data_path):
        records_ingested = data_service.ingest_data(data_path)
        print(f"✓ Ingested {records_ingested} records")
        return True
    else:
        print(f"✗ Data file not found: {data_path}")
        return False


def test_context_retrieval():
    """Test context retrieval from vector database."""
    print("Testing context retrieval...")

    data_service = DataIngestionService()

    # Test query
    query = "diabetes medication"
    results = data_service.search_similar(query, n_results=2)

    if results:
        print(f"✓ Retrieved {len(results)} context documents for query: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"  Document {i}: {result['document'][:100]}...")
        return True
    else:
        print(f"✗ No context retrieved for query: '{query}'")
        return False


def test_rag_prompt():
    """Test RAG prompt building."""
    print("Testing RAG prompt building...")

    llm_client = LLMClient()
    data_service = DataIngestionService()
    llm_client.set_data_service(data_service)

    query = "What medications are used for diabetes?"
    context = "Patient has Type 2 Diabetes Mellitus and takes Metformin 500mg twice daily."

    prompt = llm_client.build_rag_prompt(query, context)

    if "Clinical Context:" in prompt and "Type 2 Diabetes Mellitus" in prompt:
        print("✓ RAG prompt built successfully")
        print(f"  Prompt length: {len(prompt)} characters")
        return True
    else:
        print("✗ RAG prompt building failed")
        return False


def main():
    """Run all RAG tests."""
    print("🧪 Testing Clinical AI Gateway RAG Integration")
    print("=" * 50)

    tests = [
        test_data_ingestion,
        test_context_retrieval,
        test_rag_prompt,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All RAG integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check ChromaDB connection and data files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())