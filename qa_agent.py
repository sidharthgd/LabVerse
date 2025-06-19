# Modified qa_agent.py
import pandas as pd
from config import llm
from vector_store import build_vector_store
from config import DATA_DIR

def setup_qa():
    db = build_vector_store(DATA_DIR)
    retriever = db.as_retriever(search_kwargs={"k": 2})  # Get top 2 relevant docs
    
    def process_query(query):
        # Step 1: Get relevant documents
        docs = retriever.get_relevant_documents(query)
        
        print("\n---RETRIEVED FILES---")
        relevant_files = []
        for i, doc in enumerate(docs):
            file_path = doc.metadata["file_path"]
            print(f"{i+1}. {file_path}")
            relevant_files.append(file_path)
        
        # Step 2: If query seems to need data analysis, generate pandas code
        if needs_data_analysis(query):
            code = generate_pandas_code(query, docs)
            print("\n---GENERATED CODE---")
            print(code)
            
            # Step 3: Execute the pandas code
            result = execute_pandas_code(code, relevant_files)
            return result
        else:
            # Just return information about the relevant files
            return f"The most relevant files for your query are:\n" + "\n".join(relevant_files)
    
    return process_query

def needs_data_analysis(query):
    # Simple heuristic - you could make this more sophisticated
    analysis_keywords = ["analyze", "calculate", "compute", "plot", "chart", 
                         "average", "mean", "sum", "count", "filter", "find"]
    return any(keyword in query.lower() for keyword in analysis_keywords)

def generate_pandas_code(query, docs):
    # Build context from docs
    context = "\n".join([f"File: {doc.metadata['file_path']}\nDescription: {doc.page_content}" 
                         for doc in docs])
    
    # Call LLM to generate pandas code
    prompt = f"""
    Based on the user query and the available data files, generate Python code using pandas 
    to answer the query. The code should be executable, loading the files and performing 
    the necessary analysis. They are contained in a directory called "data".
    
    User query: {query}
    
    Available data files:
    {context}
    
    Generate only the pandas code without any explanations:
    ```python
    """
    
    response = llm.predict(prompt)
    # Extract just the code portion
    if "```" in response:
        code_parts = response.split("```")
        for part in code_parts:
            if "python" in part or any(pd_keyword in part for pd_keyword in ["import pandas", "pd."]):
                return part.replace("python\n", "").strip()
    return response

def execute_pandas_code(code, file_paths):
    try:
        # Create a local namespace with pandas already imported
        local_namespace = {"pd": pd, "file_paths": file_paths}
        
        # Execute the code
        exec(code, globals(), local_namespace)
        
        # Look for a result variable - this is a simple approach
        # In a more sophisticated system, you might want to capture
        # stdout or have the code return a specific variable
        result = None
        for var_name in ["result", "df", "output", "answer"]:
            if var_name in local_namespace:
                result = local_namespace[var_name]
                break
        
        return result
    except Exception as e:
        return f"Error executing code: {str(e)}"