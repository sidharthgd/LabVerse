"""
Clarifier for LabVerse Agent

Checks if sufficient information is available and asks follow-up questions if needed.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum
from .intent_classifier import IntentType
from .session import UserSession


class ClarificationStatus(str, Enum):
    """Status of clarification check."""
    READY = "ready"
    CLARIFICATION_NEEDED = "clarification_needed"
    AMBIGUOUS = "ambiguous"


class ClarificationResult(BaseModel):
    """Result of clarification check."""
    status: ClarificationStatus
    question: Optional[str] = None
    suggestions: List[str] = []
    missing_info: List[str] = []
    confidence: float = 1.0


class Clarifier:
    """
    Checks if user query has sufficient information to proceed.
    
    Identifies missing information like:
    - File not specified or multiple matches
    - Column mentioned not found
    - Action unclear or ambiguous
    """
    
    def __init__(self, available_files: List[str] = None, file_schemas: Dict[str, List[str]] = None):
        self.available_files = available_files or []
        self.file_schemas = file_schemas or {}
    
    def check_clarification_needed(self, 
                                  query: str,
                                  intent: IntentType,
                                  entities: Dict[str, Any],
                                  session: Optional[UserSession] = None) -> ClarificationResult:
        """
        Check if clarification is needed for the query.
        
        Args:
            query: User query string
            intent: Classified intent
            entities: Extracted entities
            session: User session for context
            
        Returns:
            ClarificationResult indicating if clarification is needed
        """
        missing_info = []
        suggestions = []
        
        # Check file specification
        file_check = self._check_file_specification(entities, session)
        if file_check:
            missing_info.extend(file_check["missing"])
            suggestions.extend(file_check["suggestions"])
        
        # Check column specification for data operations
        if intent in [IntentType.DATA_VISUALIZATION, IntentType.STATISTICAL_ANALYSIS, IntentType.DATA_CLEANING]:
            column_check = self._check_column_specification(entities, session)
            if column_check:
                missing_info.extend(column_check["missing"])
                suggestions.extend(column_check["suggestions"])
        
        # Check statistical method specification
        if intent == IntentType.STATISTICAL_ANALYSIS:
            method_check = self._check_statistical_method_specification(entities)
            if method_check:
                missing_info.extend(method_check["missing"])
                suggestions.extend(method_check["suggestions"])
        
        # Check visualization type specification
        if intent == IntentType.DATA_VISUALIZATION:
            viz_check = self._check_visualization_specification(entities)
            if viz_check:
                missing_info.extend(viz_check["missing"])
                suggestions.extend(viz_check["suggestions"])
        
        # Determine status and generate question
        if missing_info:
            question = self._generate_clarification_question(missing_info, suggestions, intent)
            return ClarificationResult(
                status=ClarificationStatus.CLARIFICATION_NEEDED,
                question=question,
                suggestions=suggestions,
                missing_info=missing_info,
                confidence=0.8
            )
        
        return ClarificationResult(status=ClarificationStatus.READY)
    
    def _check_file_specification(self, entities: Dict[str, Any], session: Optional[UserSession]) -> Optional[Dict[str, List[str]]]:
        """Check if file specification is clear."""
        mentioned_files = entities.get("files", [])
        
        # If no files mentioned, check session context
        if not mentioned_files and session:
            focused_files = session.get_file_context_summary()["focused_files"]
            if not focused_files:
                return {
                    "missing": ["file_specification"],
                    "suggestions": [f"Available files: {', '.join(self.available_files[:5])}"]
                }
        
        # If files mentioned, check if they exist
        elif mentioned_files:
            existing_files = []
            for file in mentioned_files:
                matches = [f for f in self.available_files if file.lower() in f.lower()]
                if matches:
                    existing_files.extend(matches)
            
            if not existing_files:
                return {
                    "missing": ["valid_file"],
                    "suggestions": [f"Did you mean: {', '.join(self.available_files[:3])}?"]
                }
            elif len(existing_files) > 1:
                return {
                    "missing": ["specific_file"],
                    "suggestions": [f"Multiple files match. Please specify: {', '.join(existing_files)}"]
                }
        
        return None
    
    def _check_column_specification(self, entities: Dict[str, Any], session: Optional[UserSession]) -> Optional[Dict[str, List[str]]]:
        """Check if column specification is clear."""
        mentioned_columns = entities.get("columns", [])
        
        if not mentioned_columns:
            return {
                "missing": ["column_specification"],
                "suggestions": ["Please specify which columns or variables to analyze"]
            }
        
        # Check if columns exist in available schemas
        if self.file_schemas:
            valid_columns = []
            for file_path, columns in self.file_schemas.items():
                for mentioned_col in mentioned_columns:
                    matches = [c for c in columns if mentioned_col.lower() in c.lower()]
                    valid_columns.extend(matches)
            
            if not valid_columns:
                available_cols = []
                for columns in self.file_schemas.values():
                    available_cols.extend(columns[:3])  # Show first 3 columns per file
                
                return {
                    "missing": ["valid_columns"],
                    "suggestions": [f"Available columns: {', '.join(set(available_cols))}"]
                }
        
        return None
    
    def _check_statistical_method_specification(self, entities: Dict[str, Any]) -> Optional[Dict[str, List[str]]]:
        """Check if statistical method is specified when needed."""
        mentioned_methods = entities.get("statistical_methods", [])
        
        if not mentioned_methods:
            return {
                "missing": ["statistical_method"],
                "suggestions": ["Available methods: t-test, ANOVA, correlation, regression, chi-square"]
            }
        
        return None
    
    def _check_visualization_specification(self, entities: Dict[str, Any]) -> Optional[Dict[str, List[str]]]:
        """Check if visualization type is clear."""
        mentioned_viz = entities.get("visualization_types", [])
        
        if not mentioned_viz:
            return {
                "missing": ["visualization_type"],
                "suggestions": ["Available plots: histogram, scatter, boxplot, heatmap, bar chart"]
            }
        
        return None
    
    def _generate_clarification_question(self, missing_info: List[str], suggestions: List[str], intent: IntentType) -> str:
        """Generate a clarification question based on missing information."""
        if "file_specification" in missing_info:
            return f"Which file would you like to analyze? {suggestions[0] if suggestions else ''}"
        
        elif "valid_file" in missing_info:
            return f"I couldn't find that file. {suggestions[0] if suggestions else ''}"
        
        elif "specific_file" in missing_info:
            return f"Multiple files match your request. {suggestions[0] if suggestions else ''}"
        
        elif "column_specification" in missing_info:
            return f"Which columns or variables would you like to analyze? {suggestions[0] if suggestions else ''}"
        
        elif "valid_columns" in missing_info:
            return f"I couldn't find those columns. {suggestions[0] if suggestions else ''}"
        
        elif "statistical_method" in missing_info:
            return f"Which statistical test would you like to perform? {suggestions[0] if suggestions else ''}"
        
        elif "visualization_type" in missing_info:
            return f"What type of plot would you like to create? {suggestions[0] if suggestions else ''}"
        
        else:
            return "Could you provide more details about what you'd like to do?"
    
    def update_available_files(self, files: List[str]):
        """Update the list of available files."""
        self.available_files = files
    
    def update_file_schemas(self, schemas: Dict[str, List[str]]):
        """Update the file schemas."""
        self.file_schemas = schemas 