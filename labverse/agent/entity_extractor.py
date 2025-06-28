"""
Entity Extraction for LabVerse Agent

Advanced entity extraction for laboratory data analysis queries.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel
import re
import spacy
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class Entity(BaseModel):
    """Represents an extracted entity."""
    text: str
    label: str
    confidence: float
    start_pos: int = 0
    end_pos: int = 0
    metadata: Dict[str, Any] = {}


class EntityExtractionResult(BaseModel):
    """Result of entity extraction."""
    entities: List[Entity]
    structured_entities: Dict[str, List[str]]
    confidence: float


class EntityExtractor:
    """
    Advanced entity extractor for laboratory data analysis queries.
    
    Extracts:
    - File names and references
    - Column names and data fields
    - Statistical methods and parameters
    - Filter conditions and values
    - Laboratory-specific terms
    - Numerical values and units
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm
        self._setup_patterns()
        self._load_nlp_model()
    
    def _load_nlp_model(self):
        """Load spaCy NLP model if available."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy English model not found. Using pattern-based extraction only.")
            self.nlp = None
    
    def _setup_patterns(self):
        """Setup extraction patterns for different entity types."""
        self.patterns = {
            "files": [
                r'\b(\w+\.(csv|xlsx?|json|txt|tsv|pdf))\b',
                r'\bfile\s+["\']?(\w+)["\']?',
                r'\bdataset\s+["\']?(\w+)["\']?',
                r'\btable\s+["\']?(\w+)["\']?'
            ],
            "columns": [
                r'\bcolumn\s+["\']?(\w+)["\']?',
                r'\b["\'](\w+)["\']?\s+column\b',
                r'\bfield\s+["\']?(\w+)["\']?',
                r'\bvariable\s+["\']?(\w+)["\']?',
                # Laboratory-specific columns
                r'\b(glucose|cholesterol|hemoglobin|creatinine|albumin|bun|sodium|potassium)\b',
                r'\b(patient_?id|sample_?id|test_?date|result_?value)\b'
            ],
            "statistical_methods": [
                r'\b(t-test|ttest|student\'?s t-test)\b',
                r'\b(anova|analysis of variance)\b',
                r'\b(correlation|pearson|spearman)\b',
                r'\b(regression|linear regression|logistic regression)\b',
                r'\b(chi-square|chi squared|χ²)\b',
                r'\b(mann-whitney|wilcoxon)\b',
                r'\b(normality test|shapiro-wilk|kolmogorov-smirnov)\b'
            ],
            "visualization_types": [
                r'\b(histogram|hist)\b',
                r'\b(scatter plot|scatterplot|scatter)\b',
                r'\b(box plot|boxplot|box)\b',
                r'\b(heat map|heatmap)\b',
                r'\b(bar chart|bar graph|barplot)\b',
                r'\b(line plot|line chart|lineplot)\b',
                r'\b(violin plot|violinplot)\b'
            ],
            "operations": [
                r'\b(filter|remove|exclude|include)\b',
                r'\b(group by|aggregate|sum|mean|average|count)\b',
                r'\b(sort|order by|rank)\b',
                r'\b(merge|join|combine|concatenate)\b',
                r'\b(clean|normalize|standardize|transform)\b'
            ],
            "numerical_values": [
                r'\b(\d+(?:\.\d+)?)\s*([%]|percent|mg/dl|mmol/l|units?|μmol/l)\b',
                r'\b(\d+(?:\.\d+)?)\b'
            ],
            "comparisons": [
                r'\b(greater than|more than|above|over)\s*(\d+(?:\.\d+)?)\b',
                r'\b(less than|below|under)\s*(\d+(?:\.\d+)?)\b',
                r'\b(equals?|equal to)\s*(\d+(?:\.\d+)?)\b',
                r'\b(between)\s*(\d+(?:\.\d+)?)\s*and\s*(\d+(?:\.\d+)?)\b'
            ],
            "time_references": [
                r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
                r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
                r'\b(last|previous|past)\s+(week|month|year|day)\b',
                r'\b(this|current)\s+(week|month|year|day)\b'
            ],
            "laboratory_terms": [
                r'\b(reference range|normal range|abnormal|out of range)\b',
                r'\b(lab results?|test results?|panel|screening)\b',
                r'\b(patient|subject|participant|sample)\b',
                r'\b(biomarker|analyte|assay|measurement)\b'
            ]
        }
    
    def extract_entities(self, 
                        query: str, 
                        context: Optional[Dict[str, Any]] = None) -> EntityExtractionResult:
        """
        Extract entities from user query.
        
        Args:
            query: User query string
            context: Optional context (available files, columns, etc.)
            
        Returns:
            EntityExtractionResult with extracted entities
        """
        entities = []
        
        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(query)
        entities.extend(pattern_entities)
        
        # NLP-based extraction (if spaCy is available)
        if self.nlp:
            nlp_entities = self._extract_with_nlp(query)
            entities.extend(nlp_entities)
        
        # Context-based validation and enhancement
        if context:
            entities = self._validate_with_context(entities, context)
        
        # LLM-based extraction for complex cases
        if self.llm and len(entities) < 3:  # If few entities found
            llm_entities = self._extract_with_llm(query, context)
            entities.extend(llm_entities)
        
        # Remove duplicates and merge similar entities
        entities = self._merge_entities(entities)
        
        # Structure entities by type
        structured = self._structure_entities(entities)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(entities)
        
        return EntityExtractionResult(
            entities=entities,
            structured_entities=structured,
            confidence=confidence
        )
    
    def _extract_with_patterns(self, query: str) -> List[Entity]:
        """Extract entities using regex patterns."""
        entities = []
        query_lower = query.lower()
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query_lower)
                for match in matches:
                    # Handle different capture group structures
                    if match.groups():
                        text = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                    else:
                        text = match.group(0)
                    
                    entities.append(Entity(
                        text=text,
                        label=entity_type,
                        confidence=0.8,  # High confidence for pattern matches
                        start_pos=match.start(),
                        end_pos=match.end()
                    ))
        
        return entities
    
    def _extract_with_nlp(self, query: str) -> List[Entity]:
        """Extract entities using spaCy NLP."""
        if not self.nlp:
            return []
        
        entities = []
        doc = self.nlp(query)
        
        # Extract named entities
        for ent in doc.ents:
            # Map spaCy labels to our entity types
            entity_type = self._map_spacy_label(ent.label_)
            if entity_type:
                entities.append(Entity(
                    text=ent.text,
                    label=entity_type,
                    confidence=0.7,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    metadata={"spacy_label": ent.label_}
                ))
        
        # Extract noun phrases that might be column names or concepts
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Short phrases likely to be column names
                entities.append(Entity(
                    text=chunk.text,
                    label="potential_column",
                    confidence=0.5,
                    start_pos=chunk.start_char,
                    end_pos=chunk.end_char
                ))
        
        return entities
    
    def _map_spacy_label(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to our entity types."""
        mapping = {
            "PERSON": "potential_column",  # Might be patient names/IDs
            "DATE": "time_references",
            "TIME": "time_references", 
            "CARDINAL": "numerical_values",
            "QUANTITY": "numerical_values",
            "PERCENT": "numerical_values",
            "ORG": "potential_file",  # Organization names might be file prefixes
        }
        return mapping.get(spacy_label)
    
    def _extract_with_llm(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[Entity]:
        """Extract entities using LLM for complex cases."""
        if not self.llm:
            return []
        
        context_str = ""
        if context:
            available_files = context.get("available_files", [])
            available_columns = context.get("available_columns", [])
            
            if available_files:
                context_str += f"\nAvailable files: {available_files}"
            if available_columns:
                context_str += f"\nAvailable columns: {available_columns}"
        
        system_prompt = """You are an expert at extracting entities from laboratory data analysis queries.

Extract the following types of entities:
- files: File names or references
- columns: Column names or data fields
- statistical_methods: Statistical tests or methods
- visualization_types: Types of plots or charts
- operations: Data operations or transformations
- numerical_values: Numbers with or without units
- comparisons: Comparison operators and values
- time_references: Dates or time periods
- laboratory_terms: Lab-specific terminology

Return a JSON list of entities in this format:
[
    {
        "text": "glucose",
        "label": "columns",
        "confidence": 0.9
    },
    {
        "text": "t-test", 
        "label": "statistical_methods",
        "confidence": 0.95
    }
]"""

        user_prompt = f"Query: {query}{context_str}"
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            import json
            entity_list = json.loads(response.content)
            
            entities = []
            for item in entity_list:
                entities.append(Entity(
                    text=item["text"],
                    label=item["label"],
                    confidence=item["confidence"],
                    metadata={"source": "llm"}
                ))
            
            return entities
            
        except Exception as e:
            print(f"LLM entity extraction failed: {e}")
            return []
    
    def _validate_with_context(self, entities: List[Entity], context: Dict[str, Any]) -> List[Entity]:
        """Validate and enhance entities using available context."""
        validated_entities = []
        
        available_files = context.get("available_files", [])
        available_columns = context.get("available_columns", [])
        
        for entity in entities:
            # Validate file references
            if entity.label == "files":
                # Check if file exists in available files
                matches = [f for f in available_files if entity.text.lower() in f.lower()]
                if matches:
                    entity.confidence = min(1.0, entity.confidence + 0.2)
                    entity.metadata["validated_files"] = matches
                else:
                    entity.confidence *= 0.5  # Reduce confidence if file not found
            
            # Validate column references
            elif entity.label == "columns" or entity.label == "potential_column":
                matches = [c for c in available_columns if entity.text.lower() in c.lower()]
                if matches:
                    entity.label = "columns"  # Promote potential columns to confirmed
                    entity.confidence = min(1.0, entity.confidence + 0.3)
                    entity.metadata["validated_columns"] = matches
                else:
                    entity.confidence *= 0.7
            
            validated_entities.append(entity)
        
        return validated_entities
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicates and merge similar entities."""
        merged = {}
        
        for entity in entities:
            key = (entity.text.lower(), entity.label)
            
            if key in merged:
                # Keep the entity with higher confidence
                if entity.confidence > merged[key].confidence:
                    merged[key] = entity
            else:
                merged[key] = entity
        
        return list(merged.values())
    
    def _structure_entities(self, entities: List[Entity]) -> Dict[str, List[str]]:
        """Structure entities by type."""
        structured = {}
        
        for entity in entities:
            if entity.confidence >= 0.5:  # Only include confident entities
                if entity.label not in structured:
                    structured[entity.label] = []
                structured[entity.label].append(entity.text)
        
        # Remove duplicates within each category
        for key in structured:
            structured[key] = list(set(structured[key]))
        
        return structured
    
    def _calculate_confidence(self, entities: List[Entity]) -> float:
        """Calculate overall confidence score."""
        if not entities:
            return 0.0
        
        # Weight by entity confidence and count
        total_confidence = sum(entity.confidence for entity in entities)
        avg_confidence = total_confidence / len(entities)
        
        # Bonus for having multiple types of entities
        unique_labels = len(set(entity.label for entity in entities))
        type_bonus = min(0.2, unique_labels * 0.05)
        
        return min(1.0, avg_confidence + type_bonus) 