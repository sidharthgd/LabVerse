#!/usr/bin/env python3
"""
Test script for LabVerse Agent Architecture

This script demonstrates the usage of the modular agent system.
"""

import asyncio
import os
from dotenv import load_dotenv
from config import llm, DATA_DIR
from vector_store import build_vector_store
from labverse.agent.assistant_agent import AssistantAgent

# Load environment variables
load_dotenv()

async def test_agent_pipeline():
    """Test the complete agent pipeline with example queries."""
    
    print("🔬 Testing LabVerse Agent Architecture")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("📡 Initializing agent components...")
        vector_db = build_vector_store(DATA_DIR)
        available_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.csv', '.xlsx', '.xls', '.json', '.txt', '.tsv'))]
        
        agent = AssistantAgent(
            llm=llm,
            vector_db=vector_db,
            data_dir=DATA_DIR,
            available_files=available_files
        )
        
        print(f"✅ Agent initialized with {len(available_files)} files")
        print(f"📁 Available files: {', '.join(available_files[:3])}...")
        
        # Test queries
        test_queries = [
            "Show me a summary of all available data",
            "What columns are in the glucose panel file?",
            "Create a histogram of glucose levels",
            "Perform a t-test comparing two groups",
            "Find outliers in the lab data"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🎯 Test Query {i}: {query}")
            print("-" * 60)
            
            try:
                response = await agent.run_query(query)
                
                print(f"Intent: {response.intent}")
                print(f"Confidence: {response.confidence:.2f}")
                print(f"Processing Time: {response.processing_time:.2f}s")
                print(f"Clarification Needed: {response.clarification_needed}")
                
                if response.entities:
                    print(f"Entities: {response.entities}")
                
                print(f"Response: {response.message[:200]}...")
                
                if response.code:
                    print("📝 Code Generated: Yes")
                
                if response.follow_up_suggestions:
                    print(f"💡 Suggestions: {response.follow_up_suggestions[:2]}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Test session continuity
        print(f"\n🔄 Testing Session Continuity")
        print("-" * 60)
        
        session_id = "test_session_123"
        
        # First query with session
        response1 = await agent.run_query(
            "Show me the glucose data", 
            session_id=session_id
        )
        print(f"Query 1 Response: {response1.message[:100]}...")
        
        # Follow-up query using the same session
        response2 = await agent.run_query(
            "Now create a histogram of that data",
            session_id=session_id
        )
        print(f"Query 2 Response: {response2.message[:100]}...")
        
        # Check session info
        session_info = agent.get_session_info(session_id)
        if session_info:
            print(f"Session has {len(session_info['conversation_history'])} conversation turns")
        
        print("\n✅ Agent pipeline testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        raise

def test_individual_components():
    """Test individual agent components."""
    
    print("\n🧪 Testing Individual Components")
    print("=" * 50)
    
    from labverse.agent.intent_classifier import IntentClassifier
    from labverse.agent.entity_extractor import EntityExtractor
    from labverse.agent.clarifier import Clarifier
    
    # Test Intent Classifier
    print("🎯 Testing Intent Classifier...")
    classifier = IntentClassifier(llm=llm)
    
    test_queries = [
        "Show me a histogram of glucose levels",
        "What columns are in this file?",
        "Perform a t-test between two groups",
        "Clean the data by removing outliers"
    ]
    
    for query in test_queries:
        result = classifier.classify_intent(query)
        print(f"Query: '{query}' → Intent: {result.primary_intent.value} (confidence: {result.confidence:.2f})")
    
    # Test Entity Extractor
    print("\n🔍 Testing Entity Extractor...")
    extractor = EntityExtractor(llm=llm)
    
    query = "Create a scatter plot of glucose vs age from the lab_results.csv file"
    result = extractor.extract_entities(query)
    print(f"Query: '{query}'")
    print(f"Extracted entities: {result.structured_entities}")
    
    # Test Clarifier
    print("\n❓ Testing Clarifier...")
    clarifier = Clarifier(
        available_files=["lab_results.csv", "demographics.csv"],
        file_schemas={"lab_results.csv": ["glucose", "cholesterol", "age"]}
    )
    
    from labverse.agent.intent_classifier import IntentType
    
    # Query without specifying a file
    unclear_query = "Show me a histogram"
    result = clarifier.check_clarification_needed(
        query=unclear_query,
        intent=IntentType.DATA_VISUALIZATION,
        entities={},
        session=None
    )
    
    print(f"Query: '{unclear_query}'")
    print(f"Clarification needed: {result.status}")
    if result.question:
        print(f"Question: {result.question}")

if __name__ == "__main__":
    print("🚀 Starting LabVerse Agent Tests")
    
    # Test individual components first
    test_individual_components()
    
    # Test the full pipeline
    asyncio.run(test_agent_pipeline())
    
    print("\n🎉 All tests completed!") 