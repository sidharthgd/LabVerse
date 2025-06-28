"""
Executor for LabVerse Agent

Processes LLM responses, executes code safely, and formats results.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel
import re
import sys
import traceback
from io import StringIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from contextlib import redirect_stdout, redirect_stderr


class ExecutionResult(BaseModel):
    """Result of code execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    plots_created: List[str] = []
    data_exported: List[str] = []
    execution_time: float = 0.0


class FormattedResponse(BaseModel):
    """Formatted response for the user."""
    message: str
    code: Optional[str] = None
    execution_result: Optional[str] = None
    code_type: str = "python"
    attachments: List[Dict[str, Any]] = []
    follow_up_suggestions: List[str] = []


class Executor:
    """
    Executes LLM-generated code and formats responses.
    
    Features:
    - Safe code execution with timeout and restrictions
    - Result formatting and visualization handling
    - Follow-up suggestion generation
    - Error handling and debugging support
    """
    
    def __init__(self, enable_code_execution: bool = True, timeout: int = 30):
        self.enable_code_execution = enable_code_execution
        self.timeout = timeout
        self.safe_globals = self._setup_safe_environment()
    
    def _setup_safe_environment(self) -> Dict[str, Any]:
        """Setup safe execution environment with allowed modules."""
        return {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'DataFrame': pd.DataFrame,
            'Series': pd.Series,
            'print': print,
            'len': len,
            'range': range,
            'list': list,
            'dict': dict,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
        }
    
    def process_llm_response(self, 
                           llm_response: str,
                           query: str,
                           intent: str,
                           file_paths: List[str] = None) -> FormattedResponse:
        """
        Process LLM response and format for user.
        
        Args:
            llm_response: Raw response from LLM
            query: Original user query
            intent: Classified intent
            file_paths: Available file paths for execution
            
        Returns:
            FormattedResponse with formatted output
        """
        # Extract code from response if present
        code = self._extract_code_from_response(llm_response)
        
        # Clean the response text (remove code blocks)
        message = self._clean_response_text(llm_response)
        
        # Execute code if present and enabled
        execution_result = None
        if code and self.enable_code_execution:
            exec_result = self._execute_code_safely(code, file_paths or [])
            execution_result = self._format_execution_result(exec_result)
        
        # Generate follow-up suggestions
        suggestions = self._generate_follow_up_suggestions(query, intent, code, execution_result)
        
        # Create attachments for plots, exports, etc.
        attachments = self._create_attachments(execution_result)
        
        return FormattedResponse(
            message=message,
            code=code,
            execution_result=execution_result,
            code_type="python",
            attachments=attachments,
            follow_up_suggestions=suggestions
        )
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from LLM response."""
        # Look for code blocks
        code_patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'```python(.*?)```'
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # If no code blocks, look for lines that look like Python code
        lines = response.split('\n')
        code_lines = []
        in_code_section = False
        
        for line in lines:
            stripped = line.strip()
            # Start code section indicators
            if any(keyword in stripped for keyword in ['import ', 'def ', 'pd.', 'plt.', 'sns.', 'result = ']):
                in_code_section = True
            
            if in_code_section:
                if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                    code_lines.append(line)
                elif not stripped:  # Empty line
                    code_lines.append(line)
                elif stripped.startswith('#'):  # Comment
                    code_lines.append(line)
                else:
                    # End of code section
                    break
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        return None
    
    def _clean_response_text(self, response: str) -> str:
        """Clean response text by removing code blocks."""
        # Remove code blocks
        cleaned = re.sub(r'```python.*?```', '', response, flags=re.DOTALL)
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _execute_code_safely(self, code: str, file_paths: List[str]) -> ExecutionResult:
        """Execute code in a controlled environment."""
        if not self.enable_code_execution:
            return ExecutionResult(
                success=False,
                error="Code execution is disabled"
            )
        
        start_time = pd.Timestamp.now()
        
        try:
            # Setup execution environment
            local_vars = self.safe_globals.copy()
            local_vars['file_paths'] = file_paths
            
            # Add file loading helpers
            local_vars['DATA_DIR'] = 'data'
            
            # Redirect stdout and stderr
            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Execute the code
                exec(code, local_vars, local_vars)
            
            # Get execution time
            execution_time = (pd.Timestamp.now() - start_time).total_seconds()
            
            # Capture output
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            
            # Look for result variable
            result = None
            for var_name in ['result', 'output', 'answer', 'df']:
                if var_name in local_vars:
                    result = local_vars[var_name]
                    break
            
            # Format result
            if result is not None:
                if isinstance(result, pd.DataFrame):
                    result_str = f"DataFrame with shape {result.shape}:\n{result.head(10).to_string()}"
                elif isinstance(result, (list, tuple, np.ndarray)):
                    result_str = f"Array/List with {len(result)} elements:\n{str(result)[:500]}"
                else:
                    result_str = str(result)[:1000]  # Limit output length
            else:
                result_str = stdout_output
            
            return ExecutionResult(
                success=True,
                output=result_str,
                error=stderr_output if stderr_output else None,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (pd.Timestamp.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=False,
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                execution_time=execution_time
            )
    
    def _format_execution_result(self, exec_result: ExecutionResult) -> str:
        """Format execution result for display."""
        if not exec_result.success:
            return f"❌ Execution failed:\n{exec_result.error}"
        
        result_parts = []
        
        if exec_result.output:
            result_parts.append(f"✅ Execution successful:")
            result_parts.append(exec_result.output)
        
        if exec_result.plots_created:
            result_parts.append(f"📊 Plots created: {', '.join(exec_result.plots_created)}")
        
        if exec_result.data_exported:
            result_parts.append(f"💾 Data exported: {', '.join(exec_result.data_exported)}")
        
        result_parts.append(f"⏱️ Execution time: {exec_result.execution_time:.2f}s")
        
        if exec_result.error:
            result_parts.append(f"⚠️ Warnings: {exec_result.error}")
        
        return "\n".join(result_parts)
    
    def _generate_follow_up_suggestions(self, 
                                      query: str,
                                      intent: str,
                                      code: Optional[str],
                                      execution_result: Optional[str]) -> List[str]:
        """Generate follow-up suggestions based on the analysis."""
        suggestions = []
        
        if intent == "data_visualization":
            suggestions.extend([
                "Would you like to customize the plot colors or style?",
                "Do you want to export this visualization?",
                "Should we create additional plots for comparison?"
            ])
        
        elif intent == "statistical_analysis":
            suggestions.extend([
                "Would you like to visualize these results?",
                "Do you want to perform additional statistical tests?",
                "Should we check the assumptions for this test?"
            ])
        
        elif intent == "file_summary":
            suggestions.extend([
                "Would you like to analyze specific columns?",
                "Do you want to create visualizations of this data?",
                "Should we check for data quality issues?"
            ])
        
        elif intent == "data_cleaning":
            suggestions.extend([
                "Would you like to apply these changes permanently?",
                "Do you want to analyze the cleaned data?",
                "Should we create a summary of the cleaning steps?"
            ])
        
        # Add general suggestions based on execution results
        if execution_result and "DataFrame" in execution_result:
            suggestions.append("Would you like to explore this data further?")
        
        if code and "plt." in code:
            suggestions.append("Do you want to modify the visualization?")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _create_attachments(self, execution_result: Optional[str]) -> List[Dict[str, Any]]:
        """Create attachments from execution results."""
        attachments = []
        
        if execution_result:
            # Check for plot mentions
            if "📊 Plots created:" in execution_result:
                # Extract plot filenames (this would be enhanced with actual plot detection)
                attachments.append({
                    "type": "plot",
                    "description": "Generated visualization",
                    "url": "/static/plots/latest_plot.png"
                })
            
            # Check for data exports
            if "💾 Data exported:" in execution_result:
                attachments.append({
                    "type": "data",
                    "description": "Exported data file",
                    "filename": "exported_data.csv"
                })
        
        return attachments
    
    def format_error_response(self, error_message: str, query: str) -> FormattedResponse:
        """Format error response for user."""
        return FormattedResponse(
            message=f"I encountered an error while processing your request: {error_message}",
            follow_up_suggestions=[
                "Could you please rephrase your question?",
                "Would you like me to explain what went wrong?",
                "Do you want to try a different approach?"
            ]
        )
    
    def format_clarification_response(self, clarification_question: str, suggestions: List[str]) -> FormattedResponse:
        """Format clarification response for user."""
        return FormattedResponse(
            message=clarification_question,
            follow_up_suggestions=suggestions
        ) 