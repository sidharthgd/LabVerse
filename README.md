# 🔬 LabVerse AI - Intelligent Laboratory Data Analysis

**LabVerse AI** is a comprehensive laboratory data analysis platform that brings the power of Glean AI to laboratory settings. It provides intelligent, conversational access to laboratory data with advanced analytics, visualization, and statistical capabilities.

## 🎯 Vision

LabVerse AI aims to be the **definitive Glean AI for laboratory environments**, enabling researchers, clinicians, and laboratory professionals to:

- **Ask natural language questions** about their laboratory data
- **Generate sophisticated analyses** with automatic code generation
- **Create publication-ready visualizations** instantly
- **Detect anomalies and patterns** in laboratory results
- **Perform statistical testing** with proper hypothesis validation
- **Export and share results** seamlessly

## ✨ Key Features

### 🤖 **Intelligent Query Processing**
- Natural language understanding of laboratory terminology
- Automatic intent detection (analysis, visualization, statistics, anomaly detection)
- Context-aware responses based on conversation history

### 📊 **Advanced Data Analysis**
- **Multi-format support**: CSV, Excel, JSON, TSV, TXT files
- **Laboratory-specific metadata extraction**: Patient counts, date ranges, lab parameters
- **Automatic code generation**: Pandas, NumPy, SciPy, Matplotlib
- **Statistical analysis**: T-tests, ANOVA, correlation, regression, chi-square tests

### 📈 **Data Visualization**
- Publication-quality plots and charts
- Interactive visualizations
- Automatic plot saving and sharing
- Laboratory-specific color schemes and formatting

### 🔍 **Anomaly Detection**
- Statistical outlier detection (IQR, Z-score methods)
- Clinical significance flagging
- Reference range validation
- Quality control monitoring

### 📁 **File Management**
- Drag-and-drop file upload
- Automatic indexing and metadata extraction
- File versioning and history
- Export capabilities

### 💬 **Conversational Interface**
- Real-time chat interface
- Message history and context preservation
- Quick action buttons for common queries
- File browser sidebar

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │   AI/ML Engine  │
│                 │    │                 │    │                 │
│ • Chat Interface│◄──►│ • REST API      │◄──►│ • Ollama LLM    │
│ • File Browser  │    │ • File Upload   │    │ • Vector Store  │
│ • Visualizations│    │ • Data Export   │    │ • Code Gen      │
│ • Quick Actions │    │ • Health Checks │    │ • Analysis      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Storage  │
                       │                 │
                       │ • CSV/Excel     │
                       │ • JSON/TSV      │
                       │ • Vector DB     │
                       │ • Plots/Exports │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama with Mistral model

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LabVerse
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up Ollama**
   ```bash
   ollama pull mistral
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

### Basic Queries
```
"Show me a summary of all the data"
"What's the average glucose level?"
"Find patients with abnormal cholesterol values"
"Create a correlation matrix for all numeric variables"
```

### Advanced Analysis
```
"Perform a t-test comparing glucose levels between groups"
"Detect outliers in the lab results using IQR method"
"Create a boxplot showing the distribution of hemoglobin levels"
"Run a chi-square test for categorical variables"
```

### Visualization Requests
```
"Plot the distribution of glucose levels"
"Create a scatter plot of age vs blood pressure"
"Show me a heatmap of correlation coefficients"
"Generate a time series plot of patient visits"
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
DATA_DIR=data
VECTOR_DB_DIR=chroma_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Customizing Analysis
The system can be customized for specific laboratory needs:

- **Reference ranges**: Add laboratory-specific normal values
- **Quality control**: Implement custom QC rules
- **Statistical methods**: Add domain-specific tests
- **Visualization templates**: Create laboratory-branded plots

## 📊 Supported Data Formats

| Format | Description | Features |
|--------|-------------|----------|
| CSV | Comma-separated values | Full support with metadata extraction |
| Excel | .xlsx, .xls files | Multi-sheet support, formulas |
| JSON | JavaScript Object Notation | Nested data, arrays |
| TSV | Tab-separated values | Large dataset support |
| TXT | Plain text files | Flexible delimiter detection |

## 🧪 Laboratory-Specific Features

### Metadata Extraction
- **Patient identification**: Automatic detection of patient/subject columns
- **Date ranges**: Temporal analysis capabilities
- **Lab parameters**: Test name and unit extraction
- **Reference ranges**: Clinical significance assessment

### Quality Control
- **Outlier detection**: Statistical and clinical methods
- **Data validation**: Format and range checking
- **Missing data analysis**: Pattern identification
- **Consistency checks**: Cross-reference validation

### Statistical Analysis
- **Descriptive statistics**: Mean, median, standard deviation
- **Inferential statistics**: Hypothesis testing, confidence intervals
- **Correlation analysis**: Pearson, Spearman correlations
- **Regression analysis**: Linear and logistic regression

## 🔒 Security & Privacy

- **Local processing**: All data stays on your infrastructure
- **No cloud dependencies**: Complete offline capability
- **Data encryption**: Optional encryption for sensitive data
- **Access control**: Role-based permissions (planned)

## 🚧 Roadmap

### Phase 1: Core Platform ✅
- [x] Basic query processing
- [x] Data analysis capabilities
- [x] Simple visualizations
- [x] File management

### Phase 2: Advanced Analytics 🚧
- [ ] Machine learning integration
- [ ] Predictive analytics
- [ ] Time series analysis
- [ ] Multi-modal data support

### Phase 3: Enterprise Features 📋
- [ ] User authentication
- [ ] Role-based access control
- [ ] Audit logging
- [ ] API rate limiting

### Phase 4: Laboratory Integration 📋
- [ ] LIMS integration
- [ ] Real-time data streaming
- [ ] Automated reporting
- [ ] Regulatory compliance

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for providing the local LLM capabilities
- **LangChain** for the AI/ML framework
- **FastAPI** for the robust backend API
- **React** for the modern frontend interface
- **Pandas** for powerful data manipulation
- **Matplotlib/Seaborn** for beautiful visualizations

## 📞 Support

- **Documentation**: [docs.labverse.ai](https://docs.labverse.ai)
- **Issues**: [GitHub Issues](https://github.com/your-org/labverse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/labverse/discussions)
- **Email**: support@labverse.ai

---

**LabVerse AI** - Making laboratory data analysis as simple as having a conversation. 🔬✨
