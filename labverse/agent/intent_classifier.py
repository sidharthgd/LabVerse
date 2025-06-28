"""
Intent Classification for LabVerse Agent

Classifies user queries into specific intents and extracts relevant entities.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from enum import Enum
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class IntentType(str, Enum):
    """Defined intent types for laboratory data analysis."""
    SEARCH_RETRIEVAL = "search_retrieval"
    METADATA_QUERY = "metadata_query"
    DATA_VISUALIZATION = "data_visualization"  
    STATISTICAL_ANALYSIS = "statistical_analysis"
    DATA_CLEANING = "data_cleaning"
    NEW_DATASET_GENERATION = "new_dataset_generation"
    FILE_SUMMARY = "file_summary"
    CODE_GENERATION = "code_generation"
    SCIENTIFIC_QUESTION = "scientific_question"
    ACCESS_PERMISSION = "access_permission"
    HELP_INSTRUCTION = "help_instruction"


class IntentResult(BaseModel):
    """Result of intent classification."""
    primary_intent: IntentType
    secondary_intents: List[IntentType] = []
    confidence: float
    reasoning: str
    entities: Dict[str, Any] = {}


class IntentClassifier:
    """
    Classifies user queries into laboratory data analysis intents.
    
    Uses a combination of rule-based patterns and LLM-based classification
    for robust intent detection.
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup rule-based patterns for quick intent detection."""
        self.intent_patterns = {
            IntentType.SEARCH_RETRIEVAL: [
                r'\b(find|search|look for|show me|get|retrieve)\b',
                r'\b(where is|locate|which file)\b',
                r'\b(data about|information on)\b'
            ],
            IntentType.METADATA_QUERY: [
                r'\b(what columns|column names|schema|structure)\b',
                r'\b(file info|metadata|description|properties)\b',
                r'\b(how many (rows|columns|files))\b'
            ],
            IntentType.DATA_VISUALIZATION: [
                r'\b(plot|graph|chart|visualize|show)\b',
                r'\b(histogram|scatter|boxplot|heatmap|bar chart)\b',
                r'\b(distribution|correlation matrix)\b'
            ],
            IntentType.STATISTICAL_ANALYSIS: [
                r'\b(t-test|anova|regression|correlation|chi-square)\b',
                r'\b(mean|median|std|variance|p-value|significant)\b',
                r'\b(compare|test|analyze|statistical)\b'
            ],
            IntentType.DATA_CLEANING: [
                r'\b(clean|filter|remove|outliers|missing values)\b',
                r'\b(normalize|standardize|transform)\b',
                r'\b(duplicates|null|nan|invalid)\b'
            ],
            IntentType.NEW_DATASET_GENERATION: [
                r'\b(create|generate|make|build) .*(dataset|file|table)\b',
                r'\b(combine|merge|join|aggregate)\b',
                r'\b(export|save|output)\b'
            ],
            IntentType.FILE_SUMMARY: [
                r'\b(summary|overview|describe|basic stats)\b',
                r'\b(what\'s in|contents of|about this file)\b'
            ],
            IntentType.CODE_GENERATION: [
                r'\b(code|script|function|write|generate)\b',
                r'\b(python|pandas|matplotlib|seaborn)\b'
            ],
            IntentType.SCIENTIFIC_QUESTION: [
                r'\b(hypothesis|research question|study|experiment)\b',
                r'\b(clinical|laboratory|biomarker|patient)\b'
            ],
            IntentType.ACCESS_PERMISSION: [
                r'\b(access|permission|authorize|login|auth)\b',
                r'\b(can\'t access|denied|forbidden)\b'
            ],
            IntentType.HELP_INSTRUCTION: [
                r'\b(help|how to|instructions|guide|tutorial)\b',
                r'\b(what can you do|commands|options)\b'
            ]
        }
    
    def classify_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        Classify user query intent using hybrid approach.
        
        Args:
            query: User query string
            context: Optional context from session or previous interactions
            
        Returns:
            IntentResult with classified intent and extracted entities
        """
        # First try rule-based classification
        rule_based_result = self._rule_based_classification(query)
        
        # If LLM is available and rule-based confidence is low, use LLM
        if self.llm and rule_based_result.confidence < 0.7:
            llm_result = self._llm_based_classification(query, context)
            # Use LLM result if it has higher confidence
            if llm_result.confidence > rule_based_result.confidence:
                return llm_result
        
        return rule_based_result
    
    def _rule_based_classification(self, query: str) -> IntentResult:
        """Classify intent using rule-based patterns."""
        query_lower = query.lower()
        intent_scores = {}
        
        # Score each intent based on pattern matches
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            # Default to search_retrieval if no patterns match
            return IntentResult(
                primary_intent=IntentType.SEARCH_RETRIEVAL,
                confidence=0.3,
                reasoning="No specific patterns matched, defaulting to search"
            )
        
        # Get primary intent (highest score)
        primary_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[primary_intent]
        
        # Get secondary intents (other high-scoring intents)
        secondary_intents = [
            intent for intent, score in intent_scores.items() 
            if intent != primary_intent and score >= max_score * 0.5
        ]
        
        # Calculate confidence based on score and pattern specificity
        confidence = min(0.9, max_score * 0.2 + 0.3)
        
        return IntentResult(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            reasoning=f"Rule-based classification with {max_score} pattern matches"
        )
    
    def _llm_based_classification(self, query: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """Classify intent using LLM."""
        if not self.llm:
            raise ValueError("LLM not available for classification")
        
        # Build context string
        context_str = ""
        if context:
            focused_files = context.get("focused_files", [])
            if focused_files:
                context_str = f"\nCurrent files in focus: {[f['file_name'] for f in focused_files]}"
        
        system_prompt = f"""You are an expert at classifying user intents for laboratory data analysis.

Available intent types:
- search_retrieval: Finding or retrieving specific data/files
- metadata_query: Questions about file structure, columns, properties
- data_visualization: Creating plots, charts, or visual representations
- statistical_analysis: Statistical tests, calculations, comparisons
- data_cleaning: Filtering, cleaning, transforming data
- new_dataset_generation: Creating new datasets, combining data
- file_summary: Getting overviews or summaries of data
- code_generation: Generating code or scripts
- scientific_question: Research questions or hypotheses
- access_permission: Authentication or access issues
- help_instruction: Asking for help or instructions

Classify the user query into one primary intent and any relevant secondary intents.
Also extract any entities like file names, column names, statistical methods, etc.

Respond in this exact JSON format:
{{
    "primary_intent": "intent_name",
    "secondary_intents": ["intent1", "intent2"],
    "confidence": 0.85,
    "reasoning": "Explanation of classification",
    "entities": {{
        "files": ["file1.csv"],
        "columns": ["column1", "column2"],
        "methods": ["t-test"],
        "filters": {{"column": "value"}}
    }}
}}"""

        user_prompt = f"User query: {query}{context_str}"
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse JSON response
            import json
            result_dict = json.loads(response.content)
            
            return IntentResult(
                primary_intent=IntentType(result_dict["primary_intent"]),
                secondary_intents=[IntentType(intent) for intent in result_dict.get("secondary_intents", [])],
                confidence=result_dict["confidence"],
                reasoning=result_dict["reasoning"],
                entities=result_dict.get("entities", {})
            )
            
        except Exception as e:
            # Fallback to rule-based if LLM fails
            print(f"LLM classification failed: {e}")
            return self._rule_based_classification(query)
    
    def extract_entities(self, query: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extract entities relevant to the classified intent.
        
        Args:
            query: User query string
            intent: Classified intent type
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract file references
        file_patterns = [
            r'(\w+\.(csv|xlsx?|json|txt|tsv))',
            r'file\s+(\w+)',
            r'dataset\s+(\w+)'
        ]
        
        files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    files.extend([match[0] for match in matches])
                else:
                    files.extend(matches)
        
        if files:
            entities["files"] = list(set(files))
        
        # Extract column references
        column_patterns = [
            r'column\s+["\']?(\w+)["\']?',
            r'["\'](\w+)["\']?\s+column',
            r'(\w+)\s+values?'
        ]
        
        columns = []
        for pattern in column_patterns:
            matches = re.findall(pattern, query_lower)
            columns.extend(matches)
        
        if columns:
            entities["columns"] = list(set(columns))
        
        # Intent-specific entity extraction
        if intent == IntentType.STATISTICAL_ANALYSIS:
            stat_methods = re.findall(r'\b(t-test|anova|regression|correlation|chi-square|mann-whitney)\b', query_lower)
            if stat_methods:
                entities["statistical_methods"] = stat_methods
        
        elif intent == IntentType.DATA_VISUALIZATION:
            viz_types = re.findall(r'\b(histogram|scatter|boxplot|heatmap|bar chart|line plot)\b', query_lower)
            if viz_types:
                entities["visualization_types"] = viz_types
        
        elif intent == IntentType.DATA_CLEANING:
            cleaning_operations = re.findall(r'\b(remove|filter|clean|normalize|standardize)\b', query_lower)
            if cleaning_operations:
                entities["operations"] = cleaning_operations
        
        # Extract filters/conditions
        filter_patterns = [
            r'where\s+(\w+)\s*(=|>|<|>=|<=)\s*(["\']?\w+["\']?)',
            r'(\w+)\s*(equals?|greater than|less than)\s*(["\']?\w+["\']?)'
        ]
        
        filters = {}
        for pattern in filter_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if len(match) == 3:
                    column, operator, value = match
                    filters[column] = {"operator": operator, "value": value.strip("\"'")}
        
        if filters:
            entities["filters"] = filters
        
        return entities 