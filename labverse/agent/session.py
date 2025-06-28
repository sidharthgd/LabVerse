"""
User Session Management for LabVerse Agent

Manages conversation context, file focus, applied filters, and interaction history.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class FileContext(BaseModel):
    """Context information for a focused file."""
    file_path: str
    file_name: str
    columns: List[str] = []
    applied_filters: Dict[str, Any] = {}
    last_accessed: datetime = Field(default_factory=datetime.now)


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""
    turn_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_query: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = {}
    clarification_needed: bool = False
    clarification_question: Optional[str] = None
    ai_response: Optional[str] = None
    code_generated: Optional[str] = None
    execution_result: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class UserSession:
    """
    Manages user session state, conversation history, and context.
    
    This class maintains:
    - Conversation history with full context
    - Currently focused files and their states
    - Applied filters and transformations
    - User preferences and settings
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Conversation state
        self.conversation_history: List[ConversationTurn] = []
        self.current_turn: Optional[ConversationTurn] = None
        
        # File and data context
        self.focused_files: Dict[str, FileContext] = {}
        self.global_filters: Dict[str, Any] = {}
        self.last_analysis_results: Optional[Dict[str, Any]] = None
        
        # User preferences
        self.preferences = {
            "visualization_style": "matplotlib",
            "statistical_significance_level": 0.05,
            "max_display_rows": 100,
            "preferred_file_format": "csv"
        }
    
    def start_new_turn(self, user_query: str) -> ConversationTurn:
        """Start a new conversation turn."""
        self.current_turn = ConversationTurn(user_query=user_query)
        self.last_activity = datetime.now()
        return self.current_turn
    
    def complete_turn(self, 
                     intent: str,
                     entities: Dict[str, Any],
                     ai_response: str,
                     code_generated: Optional[str] = None,
                     execution_result: Optional[str] = None,
                     clarification_needed: bool = False,
                     clarification_question: Optional[str] = None):
        """Complete the current conversation turn."""
        if not self.current_turn:
            raise ValueError("No active conversation turn")
        
        self.current_turn.intent = intent
        self.current_turn.entities = entities
        self.current_turn.ai_response = ai_response
        self.current_turn.code_generated = code_generated
        self.current_turn.execution_result = execution_result
        self.current_turn.clarification_needed = clarification_needed
        self.current_turn.clarification_question = clarification_question
        
        # Add to history
        self.conversation_history.append(self.current_turn)
        self.current_turn = None
        self.last_activity = datetime.now()
    
    def add_file_focus(self, file_path: str, file_name: str, columns: List[str]):
        """Add or update a file in the current focus."""
        self.focused_files[file_path] = FileContext(
            file_path=file_path,
            file_name=file_name,
            columns=columns
        )
    
    def apply_file_filter(self, file_path: str, filter_name: str, filter_value: Any):
        """Apply a filter to a specific file."""
        if file_path in self.focused_files:
            self.focused_files[file_path].applied_filters[filter_name] = filter_value
    
    def apply_global_filter(self, filter_name: str, filter_value: Any):
        """Apply a global filter across all files."""
        self.global_filters[filter_name] = filter_value
    
    def get_conversation_context(self, last_n_turns: int = 5) -> List[ConversationTurn]:
        """Get recent conversation context."""
        return self.conversation_history[-last_n_turns:] if self.conversation_history else []
    
    def get_file_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current file context."""
        return {
            "focused_files": [
                {
                    "file_name": fc.file_name,
                    "file_path": fc.file_path,
                    "columns": fc.columns,
                    "applied_filters": fc.applied_filters
                }
                for fc in self.focused_files.values()
            ],
            "global_filters": self.global_filters,
            "total_files": len(self.focused_files)
        }
    
    def clear_file_focus(self):
        """Clear all focused files."""
        self.focused_files.clear()
        self.global_filters.clear()
    
    def update_preference(self, key: str, value: Any):
        """Update a user preference."""
        self.preferences[key] = value
    
    def get_similar_past_queries(self, current_query: str, limit: int = 3) -> List[ConversationTurn]:
        """Find similar past queries for context (simple keyword matching for now)."""
        current_lower = current_query.lower()
        similar_turns = []
        
        for turn in reversed(self.conversation_history):
            if turn.ai_response:  # Only completed turns
                query_lower = turn.user_query.lower()
                # Simple keyword overlap scoring
                current_words = set(current_lower.split())
                query_words = set(query_lower.split())
                overlap = len(current_words.intersection(query_words))
                
                if overlap >= 2:  # At least 2 overlapping words
                    similar_turns.append(turn)
                    
                if len(similar_turns) >= limit:
                    break
        
        return similar_turns
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "conversation_history": [turn.dict() for turn in self.conversation_history],
            "focused_files": {k: v.dict() for k, v in self.focused_files.items()},
            "global_filters": self.global_filters,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary."""
        session = cls(session_id=data["session_id"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_activity = datetime.fromisoformat(data["last_activity"])
        
        # Restore conversation history
        session.conversation_history = [
            ConversationTurn(**turn_data) for turn_data in data["conversation_history"]
        ]
        
        # Restore file context
        session.focused_files = {
            k: FileContext(**v) for k, v in data["focused_files"].items()
        }
        
        session.global_filters = data["global_filters"]
        session.preferences = data["preferences"]
        
        return session 