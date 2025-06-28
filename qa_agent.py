# Enhanced qa_agent.py for Laboratory AI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
import json
import re
from config import llm, get_llm_for_task
from vector_store import build_vector_store
from config import DATA_DIR

# Set matplotlib to use non-interactive backend for server environment
plt.switch_backend('Agg')

class LaboratoryAI:
    def __init__(self):
        try:
            self.db = build_vector_store(DATA_DIR)
            self.retriever = self.db.as_retriever(search_kwargs={"k": 3})  # Get top 3 relevant docs
            self.conversation_history = []
            print("✅ LaboratoryAI initialized successfully with OpenAI")
        except Exception as e:
            print(f"Error initializing LaboratoryAI: {e}")
            print("💡 Make sure your OPENAI_API_KEY is set correctly")
            raise
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main query processing function with enhanced laboratory intelligence."""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": query})
            
            # Step 1: Get relevant documents
            docs = self.retriever.get_relevant_documents(query)
            
            print("\n---RETRIEVED FILES---")
            relevant_files = []
            for i, doc in enumerate(docs):
                file_path = doc.metadata["file_path"]
                print(f"{i+1}. {file_path}")
                relevant_files.append(file_path)
            
            # Step 2: Analyze query intent
            intent = self._analyze_query_intent(query)
            print(f"\n---QUERY INTENT: {intent}---")
            
            # Step 3: Process based on intent
            if intent == "data_analysis":
                result = self._perform_data_analysis(query, docs, relevant_files)
            elif intent == "statistical_test":
                result = self._perform_statistical_analysis(query, docs, relevant_files)
            elif intent == "data_visualization":
                result = self._create_visualization(query, docs, relevant_files)
            elif intent == "data_summary":
                result = self._provide_data_summary(query, docs, relevant_files)
            elif intent == "anomaly_detection":
                result = self._detect_anomalies(query, docs, relevant_files)
            else:
                result = self._provide_information(query, docs, relevant_files)
            
            # Ensure result is always a dictionary with the expected structure
            if isinstance(result, str):
                result = {"message": result, "code": None, "execution_result": None}
            elif not isinstance(result, dict):
                result = {"message": str(result), "code": None, "execution_result": None}
            
            # Add response to conversation history
            response_text = result.get("message", str(result))
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            if "api key" in str(e).lower():
                error_msg += "\n💡 Please check your OpenAI API key configuration"
            elif "rate limit" in str(e).lower():
                error_msg += "\n💡 Rate limit exceeded. Please wait a moment and try again"
            elif "insufficient_quota" in str(e).lower():
                error_msg += "\n💡 OpenAI API quota exceeded. Please check your billing"
            
            print(f"❌ {error_msg}")
            return {"message": error_msg, "code": None, "execution_result": None}
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze the intent of the user query."""
        query_lower = query.lower()
        
        # Statistical analysis keywords
        if any(word in query_lower for word in ["t-test", "anova", "correlation", "regression", "chi-square", "statistical", "significance"]):
            return "statistical_test"
        
        # Visualization keywords
        if any(word in query_lower for word in ["plot", "chart", "graph", "visualize", "histogram", "scatter", "boxplot", "heatmap"]):
            return "data_visualization"
        
        # Anomaly detection keywords
        if any(word in query_lower for word in ["anomaly", "outlier", "abnormal", "unusual", "detect", "flag"]):
            return "anomaly_detection"
        
        # Data summary keywords
        if any(word in query_lower for word in ["summary", "overview", "describe", "summary statistics", "basic stats"]):
            return "data_summary"
        
        # General analysis keywords
        if any(word in query_lower for word in ["analyze", "calculate", "compute", "find", "filter", "compare", "average", "mean", "sum", "count"]):
            return "data_analysis"
        
        return "information"
    
    def _perform_data_analysis(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Perform data analysis using generated pandas code."""
        try:
            # Use analysis model for complex data tasks
            analysis_llm = get_llm_for_task("analysis")
            code = self._generate_enhanced_pandas_code(query, docs, analysis_llm)
            print("\n---GENERATED CODE---")
            print(code)
            
            result = self._execute_pandas_code(code, file_paths)
            
            return {
                "message": "Data analysis completed successfully.",
                "code": code,
                "execution_result": result,
                "code_type": "python"
            }
        except Exception as e:
            return {
                "message": f"Data analysis failed: {str(e)}",
                "code": None,
                "execution_result": None
            }
    
    def _perform_statistical_analysis(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Perform statistical analysis with proper hypothesis testing."""
        try:
            analysis_llm = get_llm_for_task("analysis")
            code = self._generate_statistical_code(query, docs, analysis_llm)
            print("\n---GENERATED STATISTICAL CODE---")
            print(code)
            
            result = self._execute_pandas_code(code, file_paths)
            
            return {
                "message": "Statistical analysis completed successfully.",
                "code": code,
                "execution_result": result,
                "code_type": "python"
            }
        except Exception as e:
            return {
                "message": f"Statistical analysis failed: {str(e)}",
                "code": None,
                "execution_result": None
            }
    
    def _create_visualization(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Create data visualizations."""
        try:
            analysis_llm = get_llm_for_task("detailed")
            code = self._generate_visualization_code(query, docs, analysis_llm)
            print("\n---GENERATED VISUALIZATION CODE---")
            print(code)
            
            result = self._execute_visualization_code(code, file_paths)
            
            return {
                "message": "Visualization created successfully.",
                "code": code,
                "execution_result": result,
                "code_type": "python"
            }
        except Exception as e:
            return {
                "message": f"Visualization failed: {str(e)}",
                "code": None,
                "execution_result": None
            }
    
    def _detect_anomalies(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Detect anomalies in laboratory data."""
        try:
            analysis_llm = get_llm_for_task("analysis")
            code = self._generate_anomaly_detection_code(query, docs, analysis_llm)
            print("\n---GENERATED ANOMALY DETECTION CODE---")
            print(code)
            
            result = self._execute_pandas_code(code, file_paths)
            
            return {
                "message": "Anomaly detection completed successfully.",
                "code": code,
                "execution_result": result,
                "code_type": "python"
            }
        except Exception as e:
            return {
                "message": f"Anomaly detection failed: {str(e)}",
                "code": None,
                "execution_result": None
            }
    
    def _provide_data_summary(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Provide comprehensive data summaries."""
        summaries = []
        for file_path in file_paths:
            try:
                df = self._load_dataframe(file_path)
                summary = self._generate_dataframe_summary(df, file_path)
                summaries.append(summary)
            except Exception as e:
                summaries.append(f"Error processing {file_path}: {str(e)}")
        
        result_text = "\n\n".join(summaries)
        return {
            "message": result_text,
            "code": None,
            "execution_result": None
        }
    
    def _provide_information(self, query: str, docs: List, file_paths: List[str]) -> Dict[str, Any]:
        """Provide information about relevant files."""
        info = []
        for doc in docs:
            metadata = doc.metadata
            file_info = f"📁 **{metadata['file_name']}**\n"
            file_info += f"   - Path: {metadata['file_path']}\n"
            if 'columns' in metadata:
                file_info += f"   - Columns: {metadata['columns']}\n"
            if 'lab_metadata' in metadata and metadata['lab_metadata']:
                lab_meta = metadata['lab_metadata']
                if lab_meta.get('data_type') != 'unknown':
                    file_info += f"   - Type: {lab_meta['data_type']}\n"
                if lab_meta.get('patient_count', 0) > 0:
                    file_info += f"   - Patients: {lab_meta['patient_count']}\n"
            info.append(file_info)
        
        result_text = "**Relevant Files Found:**\n\n" + "\n".join(info)
        return {
            "message": result_text,
            "code": None,
            "execution_result": None
        }
    
    def _generate_enhanced_pandas_code(self, query: str, docs: List, model_llm=None) -> str:
        """Generate enhanced pandas code with laboratory context."""
        if model_llm is None:
            model_llm = llm
            
        context = self._build_context_from_docs(docs)
        
        prompt = f"""
        You are a laboratory data analyst. Generate Python code using pandas to answer the user query.
        The code should be executable and include proper error handling.
        
        User query: {query}
        
        Available data files and their context:
        {context}
        
        Requirements:
        1. Load the appropriate data files
        2. Perform the requested analysis
        3. Store the result in a variable called 'result'
        4. Include proper error handling
        5. For laboratory data, consider units, reference ranges, and clinical significance
        
        Generate only the Python code:
        ```python
        """
        
        try:
            response = model_llm.predict(prompt)
            return self._extract_code_from_response(response)
        except Exception as e:
            print(f"Error generating pandas code: {e}")
            return "result = 'Error generating analysis code'"

    def _generate_statistical_code(self, query: str, docs: List, model_llm=None) -> str:
        """Generate statistical analysis code."""
        if model_llm is None:
            model_llm = llm
            
        context = self._build_context_from_docs(docs)
        
        prompt = f"""
        You are a biostatistician analyzing laboratory data. Generate Python code for statistical analysis.
        
        User query: {query}
        
        Available data files:
        {context}
        
        Requirements:
        1. Use scipy.stats for statistical tests
        2. Include proper hypothesis testing
        3. Calculate p-values and effect sizes where appropriate
        4. Consider normality assumptions for parametric tests
        5. Store results in 'result' variable
        
        Generate only the Python code:
        ```python
        """
        
        try:
            response = model_llm.predict(prompt)
            return self._extract_code_from_response(response)
        except Exception as e:
            print(f"Error generating statistical code: {e}")
            return "result = 'Error generating statistical code'"

    def _generate_visualization_code(self, query: str, docs: List, model_llm=None) -> str:
        """Generate visualization code."""
        if model_llm is None:
            model_llm = llm
            
        context = self._build_context_from_docs(docs)
        
        prompt = f"""
        You are a data visualization expert for laboratory data. Generate Python code to create appropriate visualizations.
        
        User query: {query}
        
        Available data files:
        {context}
        
        Requirements:
        1. Use matplotlib and seaborn for visualizations
        2. Create publication-quality plots
        3. Include proper labels and titles
        4. Consider color schemes appropriate for scientific data
        5. Save the plot and return the filename in 'result' variable
        
        Generate only the Python code:
        ```python
        """
        
        try:
            response = model_llm.predict(prompt)
            return self._extract_code_from_response(response)
        except Exception as e:
            print(f"Error generating visualization code: {e}")
            return "result = 'Error generating visualization code'"

    def _generate_anomaly_detection_code(self, query: str, docs: List, model_llm=None) -> str:
        """Generate anomaly detection code."""
        if model_llm is None:
            model_llm = llm
            
        context = self._build_context_from_docs(docs)
        
        prompt = f"""
        You are a laboratory quality control specialist. Generate Python code to detect anomalies in laboratory data.
        
        User query: {query}
        
        Available data files:
        {context}
        
        Requirements:
        1. Use statistical methods (IQR, Z-score) for outlier detection
        2. Consider laboratory reference ranges
        3. Flag clinically significant anomalies
        4. Provide detailed analysis of detected anomalies
        5. Store results in 'result' variable
        
        Generate only the Python code:
        ```python
        """
        
        try:
            response = model_llm.predict(prompt)
            return self._extract_code_from_response(response)
        except Exception as e:
            print(f"Error generating anomaly detection code: {e}")
            return "result = 'Error generating anomaly detection code'"
    
    def _build_context_from_docs(self, docs: List) -> str:
        """Build context from retrieved documents."""
        context_parts = []
        for doc in docs:
            context_parts.append(f"File: {doc.metadata['file_path']}")
            context_parts.append(f"Description: {doc.page_content}")
            if 'lab_metadata' in doc.metadata and doc.metadata['lab_metadata']:
                lab_meta = doc.metadata['lab_metadata']
                context_parts.append(f"Lab Metadata: {json.dumps(lab_meta, indent=2)}")
        return "\n".join(context_parts)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response."""
        if "```" in response:
            code_parts = response.split("```")
            for part in code_parts:
                if "python" in part or any(keyword in part for keyword in ["import pandas", "pd.", "import matplotlib", "import seaborn"]):
                    return part.replace("python\n", "").strip()
        return response
    
    def _execute_pandas_code(self, code: str, file_paths: List[str]) -> str:
        """Execute pandas code safely."""
        try:
            # Create a local namespace with common libraries
            local_namespace = {
                "pd": pd, 
                "np": np,
                "file_paths": file_paths,
                "DATA_DIR": DATA_DIR
            }
            
            # Execute the code
            exec(code, globals(), local_namespace)
            
            # Look for result variable
            result = None
            for var_name in ["result", "df", "output", "answer"]:
                if var_name in local_namespace:
                    result = local_namespace[var_name]
                    break
            
            if result is None:
                return "Analysis completed but no result variable found."
            
            # Format the result appropriately
            if isinstance(result, pd.DataFrame):
                return f"Analysis Results:\n\n{result.to_string()}"
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            return f"Error executing code: {str(e)}"
    
    def _execute_visualization_code(self, code: str, file_paths: List[str]) -> str:
        """Execute visualization code and return plot filename."""
        try:
            local_namespace = {
                "pd": pd, 
                "np": np,
                "plt": plt,
                "sns": sns,
                "file_paths": file_paths,
                "DATA_DIR": DATA_DIR
            }
            
            exec(code, globals(), local_namespace)
            
            # Look for result (plot filename)
            result = local_namespace.get("result", "plot.png")
            return f"Visualization created: {result}"
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}"
    
    def _load_dataframe(self, file_path: str) -> pd.DataFrame:
        """Load dataframe from file path."""
        ext = file_path.split('.')[-1].lower()
        if ext == 'csv':
            return pd.read_csv(file_path)
        elif ext in ['xlsx', 'xls']:
            return pd.read_excel(file_path)
        elif ext == 'json':
            with open(file_path) as f:
                data = json.load(f)
                return pd.json_normalize(data if isinstance(data, list) else [data])
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _generate_dataframe_summary(self, df: pd.DataFrame, file_path: str) -> str:
        """Generate comprehensive dataframe summary."""
        summary = f"## Summary for {file_path}\n\n"
        summary += f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns\n\n"
        
        # Column information
        summary += "**Columns:**\n"
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            summary += f"- {col} ({dtype}, {null_count} nulls)\n"
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary += f"\n**Numeric Columns Statistics:**\n"
            summary += df[numeric_cols].describe().to_string()
        
        # Sample data
        summary += f"\n\n**Sample Data (first 3 rows):**\n"
        summary += df.head(3).to_string()
        
        return summary

def setup_qa():
    """Setup function that returns the enhanced QA agent."""
    lab_ai = LaboratoryAI()
    return lab_ai.process_query