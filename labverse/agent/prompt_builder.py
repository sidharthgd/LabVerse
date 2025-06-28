"""
Prompt Builder for LabVerse Agent

Constructs comprehensive prompts with context, schemas, and conversation history.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from .intent_classifier import IntentType
from .session import UserSession


class PromptTemplate(BaseModel):
    """Template for different types of prompts."""
    system_prompt: str
    user_template: str
    max_tokens: int = 4000


class PromptBuilder:
    """
    Builds comprehensive prompts for the LLM with relevant context.
    
    Includes:
    - File schemas and sample data
    - Conversation history
    - Task-specific instructions
    - Token limit management
    """
    
    def __init__(self):
        self._setup_templates()
    
    def _setup_templates(self):
        """Setup prompt templates for different intents."""
        self.templates = {
            IntentType.DATA_VISUALIZATION: PromptTemplate(
                system_prompt="""You are a data visualization expert for laboratory data analysis.
Create Python code using matplotlib/seaborn to generate professional, publication-quality visualizations.

Guidelines:
- Use appropriate plot types for the data
- Include proper labels, titles, and legends
- Handle missing values appropriately
- Use scientific color palettes
- Save plots with descriptive filenames
- Return the plot filename in a 'result' variable""",
                user_template="""User Request: {query}

Available Data:
{context}

Generate Python code to create the requested visualization.""",
                max_tokens=2000
            ),
            
            IntentType.STATISTICAL_ANALYSIS: PromptTemplate(
                system_prompt="""You are a biostatistician analyzing laboratory data.
Generate Python code using scipy, statsmodels, and pandas for statistical analysis.

Guidelines:
- Choose appropriate statistical tests
- Check assumptions (normality, independence, etc.)
- Calculate effect sizes and confidence intervals
- Interpret results in scientific context
- Handle multiple comparisons if needed
- Store results in a 'result' variable""",
                user_template="""User Request: {query}

Available Data:
{context}

Past Analysis Context:
{conversation_context}

Generate statistical analysis code with proper interpretation.""",
                max_tokens=3000
            ),
            
            IntentType.DATA_CLEANING: PromptTemplate(
                system_prompt="""You are a data cleaning expert for laboratory datasets.
Generate Python code using pandas to clean and preprocess data.

Guidelines:
- Handle missing values appropriately
- Detect and handle outliers
- Validate data types and ranges
- Remove duplicates if needed
- Document all cleaning steps
- Preserve data integrity""",
                user_template="""User Request: {query}

Available Data:
{context}

Generate data cleaning code with explanations.""",
                max_tokens=2000
            ),
            
            IntentType.FILE_SUMMARY: PromptTemplate(
                system_prompt="""You are a data analyst providing comprehensive summaries of laboratory datasets.
Generate clear, informative summaries that help researchers understand their data.

Guidelines:
- Describe the dataset structure and contents
- Identify key variables and their meanings
- Highlight potential quality issues
- Suggest analytical approaches
- Use domain-specific terminology""",
                user_template="""User Request: {query}

Available Data:
{context}

Provide a comprehensive summary of the dataset(s).""",
                max_tokens=1500
            )
        }
        
        # Default template for other intents
        self.default_template = PromptTemplate(
            system_prompt="""You are a laboratory data analysis assistant.
Help researchers analyze, visualize, and understand their scientific data.

Guidelines:
- Provide accurate, scientific responses
- Generate working Python code when requested
- Explain statistical concepts clearly
- Consider laboratory-specific contexts
- Be precise and professional""",
            user_template="""User Request: {query}

Available Data:
{context}

Conversation History:
{conversation_context}

Provide a helpful response or generate appropriate code.""",
            max_tokens=2500
        )
    
    def build_prompt(self, 
                    query: str,
                    intent: IntentType,
                    retrieved_context: Dict[str, Any],
                    session: Optional[UserSession] = None,
                    entities: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Build a complete prompt for the LLM.
        
        Args:
            query: User query
            intent: Classified intent
            retrieved_context: Context from retriever
            session: User session for conversation history
            entities: Extracted entities
            
        Returns:
            Dictionary with system_prompt and user_prompt
        """
        # Get appropriate template
        template = self.templates.get(intent, self.default_template)
        
        # Build context section
        context_str = self._build_context_section(retrieved_context, entities)
        
        # Build conversation context
        conversation_context = self._build_conversation_context(session)
        
        # Format the user prompt
        user_prompt = template.user_template.format(
            query=query,
            context=context_str,
            conversation_context=conversation_context,
            entities=entities or {}
        )
        
        # Ensure token limits
        user_prompt = self._truncate_to_token_limit(user_prompt, template.max_tokens)
        
        return {
            "system_prompt": template.system_prompt,
            "user_prompt": user_prompt
        }
    
    def _build_context_section(self, retrieved_context: Dict[str, Any], entities: Optional[Dict[str, Any]]) -> str:
        """Build the context section with file information."""
        if not retrieved_context.get("documents"):
            return "No specific files found. Please specify which data to analyze."
        
        context_parts = []
        
        # Add file information
        for i, doc in enumerate(retrieved_context["documents"][:3], 1):  # Limit to top 3 files
            file_info = f"File {i}: {doc['file_name']}\n"
            file_info += f"Path: {doc['file_path']}\n"
            
            if doc.get("columns"):
                file_info += f"Columns: {', '.join(doc['columns'][:10])}...\n"  # Show first 10 columns
            
            if doc.get("sample_data"):
                sample = doc["sample_data"]
                file_info += f"Shape: {sample.get('shape', 'Unknown')}\n"
                
                if sample.get("sample_rows"):
                    file_info += "Sample data:\n"
                    for row in sample["sample_rows"][:2]:  # Show 2 sample rows
                        row_str = ", ".join(f"{k}: {v}" for k, v in list(row.items())[:5])  # First 5 columns
                        file_info += f"  {row_str}\n"
            
            context_parts.append(file_info)
        
        # Add aggregated metadata
        metadata = retrieved_context.get("metadata", {})
        if metadata:
            context_parts.append(f"\nSummary: {metadata.get('total_files', 0)} files, "
                                f"{metadata.get('column_count', 0)} unique columns")
        
        return "\n".join(context_parts)
    
    def _build_conversation_context(self, session: Optional[UserSession]) -> str:
        """Build conversation context from session history."""
        if not session:
            return "No previous conversation history."
        
        recent_turns = session.get_conversation_context(last_n_turns=3)
        if not recent_turns:
            return "No previous conversation history."
        
        context_parts = []
        for turn in recent_turns:
            if turn.ai_response:
                context_parts.append(f"Previous Query: {turn.user_query}")
                context_parts.append(f"Response: {turn.ai_response[:200]}...")  # Truncate long responses
                
                if turn.code_generated:
                    context_parts.append(f"Code Generated: Yes")
                
                context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximate token limit."""
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate and add indication
        truncated = text[:max_chars-50]  # Leave room for truncation message
        truncated += "\n\n[Content truncated due to length...]"
        
        return truncated
    
    def add_custom_template(self, intent: IntentType, template: PromptTemplate):
        """Add or update a custom prompt template."""
        self.templates[intent] = template
    
    def build_clarification_prompt(self, 
                                  original_query: str,
                                  clarification_question: str,
                                  available_options: List[str]) -> Dict[str, str]:
        """Build a prompt for clarification scenarios."""
        system_prompt = """You are helping clarify a user's request for laboratory data analysis.
The user's original query was ambiguous or missing information.
Provide a clear, helpful clarification question with specific options."""
        
        user_prompt = f"""Original User Query: {original_query}

Clarification Needed: {clarification_question}

Available Options: {', '.join(available_options)}

Please provide a clear, friendly clarification question that helps the user proceed."""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
    
    def build_error_handling_prompt(self, 
                                   query: str,
                                   error_message: str,
                                   context: Dict[str, Any]) -> Dict[str, str]:
        """Build a prompt for error handling scenarios."""
        system_prompt = """You are helping resolve an error in laboratory data analysis.
Provide a clear explanation of what went wrong and suggest solutions.
Be helpful and constructive in your response."""
        
        user_prompt = f"""User Query: {query}

Error Encountered: {error_message}

Context: {context}

Please explain what went wrong and suggest how to fix it."""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        } 