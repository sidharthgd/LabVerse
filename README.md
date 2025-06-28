# LabVerse AI 🔬

**Intelligent Laboratory Data Analysis Assistant with Conversational AI Agent**

LabVerse is an AI-powered internal research assistant for scientific labs that lets users search, summarize, analyze, and manipulate research datasets (CSV, Excel, JSON, PDF) via natural language. The system features a modular, conversational agent architecture with memory, clarification capabilities, and code generation.

## 🌟 Features

### 🧠 **Intelligent Agent Architecture**
- **Intent Classification**: Automatically understands user requests (visualization, statistical analysis, data cleaning, etc.)
- **Entity Extraction**: Identifies files, columns, methods, and parameters from natural language
- **Smart Clarification**: Asks follow-up questions when information is missing or ambiguous
- **Context Memory**: Maintains conversation history and file focus across interactions
- **Hybrid Retrieval**: Combines semantic search with metadata filtering for optimal data access

### 📊 **Advanced Data Analysis**
- **Statistical Analysis**: T-tests, ANOVA, correlation, regression, chi-square tests
- **Data Visualization**: Histograms, scatter plots, boxplots, heatmaps, correlation matrices
- **Data Cleaning**: Outlier detection, missing value handling, data validation
- **Anomaly Detection**: Statistical and laboratory-specific anomaly identification
- **Code Generation**: Automatic Python/Pandas code generation with execution

### 💬 **Conversational Interface**
- Real-time chat interface with message history
- Context preservation across sessions
- Follow-up suggestions and guided workflows
- Multi-file analysis support
- Quick action buttons for common queries

## 🏗️ Architecture

### Agent Pipeline

```
User Query  
   ↓  
Intent Classifier + Entity Extractor  
   ↓  
[Is info missing?] → Clarifier → Ask follow-up  
   ↓  
Data Retriever → Contextual Prompt Builder  
   ↓  
LLM (OpenAI GPT) → Code/Answer Generator  
   ↓  
Executor → Result Output + Next-Step Suggestions
```

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │ Agent Architecture│
│                 │    │                 │    │                 │
│ • Chat Interface│◄──►│ • REST API      │◄──►│ • Intent Classifier│
│ • File Browser  │    │ • File Upload   │    │ • Entity Extractor │
│ • Visualizations│    │ • Session Mgmt  │    │ • Clarifier       │
│ • Quick Actions │    │ • Health Checks │    │ • Retriever       │
└─────────────────┘    └─────────────────┘    │ • Prompt Builder  │
                                │              │ • Executor        │
                                ▼              └─────────────────┘
                       ┌─────────────────┐              │
                       │   Data Storage  │              ▼
                       │                 │    ┌─────────────────┐
                       │ • CSV/Excel     │    │   AI/ML Engine  │
                       │ • JSON/TSV      │    │                 │
                       │ • Vector DB     │    │ • OpenAI GPT    │
                       │ • Session Store │    │ • ChromaDB      │
                       └─────────────────┘    │ • Code Execution│
                                              └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LabVerse
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   
   # Optional: Install spaCy model for enhanced entity extraction
   python -m spacy download en_core_web_sm
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   DATA_DIR=data
   VECTOR_DB_DIR=chroma_db
   ```

5. **Add your laboratory data**
   ```bash
   # Place your data files in the data/ directory
   cp your_lab_data.csv data/
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python app.py
   ```

2. **Start the frontend development server**
   ```bash
   npm run dev
   ```

3. **Open your browser**
   Navigate to `http://localhost:5173`

## 📖 Usage Examples

### Agent Architecture Queries

The new agent architecture supports natural language queries with automatic intent classification:

#### Basic Data Exploration
```
"Show me a summary of the glucose panel data"
"What columns are available in the lab results file?"
"How many patients are in the study?"
```

#### Statistical Analysis
```
"Perform a t-test comparing glucose levels between control and treatment groups"
"Calculate correlation between cholesterol and age"
"Run ANOVA to compare hemoglobin across different age groups"
```

#### Data Visualization
```
"Create a histogram of glucose levels"
"Plot blood pressure vs age with a scatter plot"
"Show me a heatmap of correlations between all lab values"
```

#### Data Cleaning
```
"Find outliers in the cholesterol data using IQR method"
"Remove rows with missing glucose values"
"Standardize all numeric columns"
```

#### Advanced Queries
```
"Which patients have abnormal glucose levels outside reference range?"
"Create a boxplot showing HDL distribution by gender and age group"
"Generate a summary report of data quality issues"
```

### API Endpoints

#### New Agent Architecture
- `POST /assistant/query` - Send queries to the intelligent agent
- `GET /assistant/sessions` - List active conversation sessions
- `GET /assistant/sessions/{id}` - Get session information
- `DELETE /assistant/sessions/{id}` - Clear a session

#### Legacy Endpoints
- `POST /chat` - Legacy chat endpoint
- `GET /files` - List available data files
- `POST /upload` - Upload new data files

## 🔧 Configuration

### Agent Components

The agent architecture is modular and configurable:

```python
from labverse.agent import AssistantAgent, IntentClassifier, EntityExtractor

# Initialize with custom configuration
agent = AssistantAgent(
    llm=your_llm_instance,
    vector_db=your_vector_db,
    data_dir="your_data_directory",
    available_files=file_list,
    file_schemas=column_schemas
)
```

### Intent Types

The system recognizes these intent types:
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

### Customizing for Your Lab

The system can be customized for specific laboratory needs:

- **Reference Ranges**: Add laboratory-specific normal values
- **Quality Control**: Implement custom QC rules
- **Statistical Methods**: Add domain-specific tests
- **Visualization Templates**: Create laboratory-branded plots

## 📊 Supported Data Formats

| Format | Description | Features |
|--------|-------------|----------|
| CSV | Comma-separated values | Full support with metadata extraction |
| Excel | .xlsx, .xls files | Multi-sheet support, formulas |
| JSON | JavaScript Object Notation | Nested data, arrays |
| TSV | Tab-separated values | Large dataset support |

## 🧪 Example Laboratory Workflows

### Quality Control Analysis
1. Upload daily QC data
2. "Check for QC failures in today's results"
3. "Plot control charts for glucose QC"
4. "Generate QC summary report"

### Research Data Analysis
1. "Compare biomarker levels between treatment groups"
2. "Are there any correlations between lab values and patient outcomes?"
3. "Create publication-ready figures for the results"
4. "Export the statistical analysis results"

### Data Validation
1. "Check for missing values in the patient data"
2. "Identify outliers in the cholesterol measurements"
3. "Validate that all patient IDs are unique"
4. "Generate a data quality report"

## 🛠️ Development

### Adding Custom Components

```python
# Add custom intent type
from labverse.agent.intent_classifier import IntentType, IntentClassifier

# Add custom prompt templates
from labverse.agent.prompt_builder import PromptBuilder, PromptTemplate

prompt_builder.add_custom_template(
    IntentType.CUSTOM_ANALYSIS,
    PromptTemplate(
        system_prompt="Your custom system prompt...",
        user_template="Your custom user template...",
        max_tokens=2000
    )
)
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt
npm install

# Run tests
python -m pytest
npm test

# Format code
black .
prettier --write src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the LLM capabilities
- **LangChain** for the AI/ML framework
- **FastAPI** for the robust backend API
- **React** for the modern frontend interface
- **ChromaDB** for vector database functionality
- **Pandas** for powerful data manipulation
- **Matplotlib/Seaborn** for beautiful visualizations

## 📞 Support

- **Documentation**: [docs.labverse.ai](https://docs.labverse.ai)
- **Issues**: [GitHub Issues](https://github.com/your-org/labverse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/labverse/discussions)
- **Email**: support@labverse.ai

---

**LabVerse AI** - Making laboratory data analysis as simple as having a conversation. 🔬✨
