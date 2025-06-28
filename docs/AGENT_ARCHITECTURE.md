# LabVerse Agent Architecture Documentation

## Overview

The LabVerse Agent Architecture is a modular, conversational AI system designed for laboratory data analysis. It implements a complete pipeline from intent classification to code execution, with memory, clarification capabilities, and context awareness.

## Architecture Components

### 1. UserSession (`labverse/agent/session.py`)

Manages conversation state and context across interactions.

**Key Features:**
- Conversation history tracking
- File focus management
- Applied filters and transformations
- User preferences storage

**Usage:**
```python
from labverse.agent.session import UserSession

session = UserSession()
session.start_new_turn("Show me glucose data")
session.add_file_focus("data/glucose.csv", "glucose.csv", ["patient_id", "glucose", "date"])
```

### 2. IntentClassifier (`labverse/agent/intent_classifier.py`)

Classifies user queries into specific intent categories using hybrid rule-based and LLM approaches.

**Supported Intents:**
- `search_retrieval` - Finding specific data/files
- `metadata_query` - Questions about data structure
- `data_visualization` - Creating plots and charts
- `statistical_analysis` - Statistical tests and calculations
- `data_cleaning` - Data preprocessing and cleaning
- `new_dataset_generation` - Creating new datasets
- `file_summary` - Data overviews and summaries
- `code_generation` - Generating analysis code
- `scientific_question` - Research questions and hypotheses
- `access_permission` - Authentication issues
- `help_instruction` - Usage help and instructions

**Usage:**
```python
from labverse.agent.intent_classifier import IntentClassifier

classifier = IntentClassifier(llm=your_llm)
result = classifier.classify_intent("Create a histogram of glucose levels")
print(result.primary_intent)  # IntentType.DATA_VISUALIZATION
```

### 3. EntityExtractor (`labverse/agent/entity_extractor.py`)

Extracts relevant entities from user queries using multiple approaches:
- Pattern-based extraction with regex
- NLP-based extraction with spaCy (optional)
- LLM-based extraction for complex cases
- Context-based validation

**Extracted Entity Types:**
- Files and datasets
- Column names and variables
- Statistical methods
- Visualization types
- Numerical values and units
- Time references
- Laboratory-specific terms

**Usage:**
```python
from labverse.agent.entity_extractor import EntityExtractor

extractor = EntityExtractor(llm=your_llm)
result = extractor.extract_entities(
    "Plot glucose vs age from lab_results.csv",
    context={"available_files": ["lab_results.csv"]}
)
```

### 4. Clarifier (`labverse/agent/clarifier.py`)

Checks if sufficient information is available to proceed and asks follow-up questions when needed.

**Clarification Scenarios:**
- File not specified or multiple matches
- Column mentioned not found
- Statistical method unclear
- Visualization type ambiguous

**Usage:**
```python
from labverse.agent.clarifier import Clarifier

clarifier = Clarifier(
    available_files=["data1.csv", "data2.csv"],
    file_schemas={"data1.csv": ["col1", "col2"]}
)

result = clarifier.check_clarification_needed(
    query="Show me a plot",
    intent=IntentType.DATA_VISUALIZATION,
    entities={},
    session=session
)
```

### 5. Retriever (`labverse/agent/retriever.py`)

Hybrid retrieval system combining semantic search with metadata filtering.

**Features:**
- ChromaDB semantic search
- Entity-based filtering
- Metadata filters (file type, date, size)
- Context-aware ranking
- Sample data enrichment

**Usage:**
```python
from labverse.agent.retriever import Retriever

retriever = Retriever(vector_db=your_vector_db, data_dir="data/")
result = retriever.retrieve_context(
    query="glucose analysis",
    entities={"files": ["glucose.csv"]},
    max_results=3
)
```

### 6. PromptBuilder (`labverse/agent/prompt_builder.py`)

Constructs comprehensive prompts for the LLM with context and conversation history.

**Features:**
- Intent-specific templates
- Context section building
- Conversation history inclusion
- Token limit management
- Customizable templates

**Usage:**
```python
from labverse.agent.prompt_builder import PromptBuilder

builder = PromptBuilder()
prompt = builder.build_prompt(
    query="Create a histogram",
    intent=IntentType.DATA_VISUALIZATION,
    retrieved_context=retrieval_result,
    session=session
)
```

### 7. Executor (`labverse/agent/executor.py`)

Processes LLM responses, executes code safely, and formats results.

**Features:**
- Code extraction from LLM responses
- Safe code execution with sandboxing
- Result formatting and visualization handling
- Follow-up suggestion generation
- Error handling and debugging

**Usage:**
```python
from labverse.agent.executor import Executor

executor = Executor(enable_code_execution=True)
response = executor.process_llm_response(
    llm_response="Here's the code...",
    query="Create histogram",
    intent="data_visualization"
)
```

### 8. AssistantAgent (`labverse/agent/assistant_agent.py`)

Main orchestration agent that coordinates the entire pipeline.

**Pipeline Flow:**
1. Session management
2. Intent classification
3. Entity extraction
4. Clarification check
5. Data retrieval
6. Prompt building
7. LLM processing
8. Result execution

**Usage:**
```python
from labverse.agent.assistant_agent import AssistantAgent

agent = AssistantAgent(
    llm=your_llm,
    vector_db=vector_db,
    data_dir="data/",
    available_files=file_list
)

response = await agent.run_query("Show me glucose statistics")
```

## Integration with FastAPI

The agent is integrated into the FastAPI backend with the following endpoints:

### New Agent Endpoints

- `POST /assistant/query` - Main query endpoint
- `GET /assistant/sessions` - List active sessions
- `GET /assistant/sessions/{id}` - Get session information
- `DELETE /assistant/sessions/{id}` - Clear session

### Request/Response Format

**Request:**
```json
{
    "query": "Create a histogram of glucose levels",
    "session_id": "optional_session_id",
    "context": {"additional": "context"}
}
```

**Response:**
```json
{
    "message": "Generated analysis response",
    "code": "import pandas as pd...",
    "execution_result": "Analysis completed successfully",
    "code_type": "python",
    "attachments": [],
    "follow_up_suggestions": ["suggestion1", "suggestion2"],
    "intent": "data_visualization",
    "entities": {"files": ["data.csv"]},
    "clarification_needed": false,
    "confidence": 0.95,
    "processing_time": 2.34
}
```

## Configuration and Customization

### Adding Custom Intent Types

```python
from labverse.agent.intent_classifier import IntentType

class CustomIntentType(str, Enum):
    CUSTOM_ANALYSIS = "custom_analysis"

# Update patterns
classifier.intent_patterns[CustomIntentType.CUSTOM_ANALYSIS] = [
    r'\b(custom|special)\b'
]
```

### Custom Prompt Templates

```python
from labverse.agent.prompt_builder import PromptTemplate

custom_template = PromptTemplate(
    system_prompt="You are a specialist in...",
    user_template="User request: {query}\nContext: {context}",
    max_tokens=2000
)

prompt_builder.add_custom_template(IntentType.CUSTOM, custom_template)
```

### Custom Entity Patterns

```python
extractor.patterns["custom_entities"] = [
    r'\b(pattern1|pattern2)\b'
]
```

## Error Handling

The architecture includes comprehensive error handling:

1. **Component-level errors**: Each component handles its own errors gracefully
2. **Pipeline errors**: The main agent catches and formats errors appropriately
3. **LLM errors**: Fallback to rule-based approaches when LLM fails
4. **Code execution errors**: Safe execution with detailed error reporting

## Performance Considerations

1. **Caching**: Results can be cached at multiple levels
2. **Parallel processing**: Multiple components can run in parallel
3. **Token limits**: Automatic truncation to stay within LLM limits
4. **Memory management**: Session cleanup and garbage collection

## Testing

Use the provided test script to verify functionality:

```bash
python test_agent.py
```

This tests:
- Individual component functionality
- Full pipeline integration
- Session continuity
- Error handling

## Future Enhancements

1. **Advanced entity linking**: Connect entities to knowledge graphs
2. **Multi-modal support**: Handle images, PDFs, and other formats
3. **Real-time learning**: Adapt to user preferences over time
4. **Collaborative features**: Multi-user sessions and sharing
5. **Advanced security**: Enhanced sandboxing and permission controls

## Troubleshooting

### Common Issues

1. **"Intent classification failed"**
   - Check LLM connectivity
   - Verify API keys
   - Fallback to rule-based classification

2. **"Entity extraction returned empty results"**
   - Install spaCy model: `python -m spacy download en_core_web_sm`
   - Check query format and available context

3. **"Code execution failed"**
   - Verify file paths and permissions
   - Check data file formats
   - Review generated code for syntax errors

4. **"Clarification loop"**
   - Check available files list
   - Verify file schemas are up to date
   - Ensure entities are properly extracted

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This architecture provides a robust, extensible foundation for intelligent laboratory data analysis with natural language interfaces. 