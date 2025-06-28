"""
Main Assistant Agent for LabVerse

Orchestrates the complete agent pipeline: Intent → Clarification → Retrieval → Prompt → LLM → Execution
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime

from .intent_classifier import IntentClassifier, IntentType
from .entity_extractor import EntityExtractor
from .clarifier import Clarifier, ClarificationStatus
from .retriever import Retriever
from .prompt_builder import PromptBuilder
from .executor import Executor, FormattedResponse
from .session import UserSession

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class AgentResponse(BaseModel):
    """Complete response from the assistant agent."""
    message: str
    code: Optional[str] = None
    execution_result: Optional[str] = None
    code_type: str = "python"
    attachments: List[Dict[str, Any]] = []
    follow_up_suggestions: List[str] = []
    
    # Agent metadata
    intent: str
    entities: Dict[str, Any] = {}
    clarification_needed: bool = False
    confidence: float = 0.0
    processing_time: float = 0.0


class AssistantAgent:
    """
    Main orchestration agent for LabVerse.
    
    Implements the complete pipeline:
    User Query → Intent Classification → Entity Extraction → Clarification Check
    → Data Retrieval → Prompt Building → LLM Processing → Result Execution
    """
    
    def __init__(self, 
                 llm: ChatOpenAI,
                 vector_db,
                 data_dir: str,
                 available_files: List[str] = None,
                 file_schemas: Dict[str, List[str]] = None):
        """
        Initialize the assistant agent.
        
        Args:
            llm: OpenAI LLM instance
            vector_db: ChromaDB vector store
            data_dir: Directory containing data files
            available_files: List of available file names
            file_schemas: Dictionary mapping file paths to column lists
        """
        self.llm = llm
        self.data_dir = data_dir
        
        # Initialize all agent components
        self.intent_classifier = IntentClassifier(llm=llm)
        self.entity_extractor = EntityExtractor(llm=llm)
        self.clarifier = Clarifier(
            available_files=available_files or [],
            file_schemas=file_schemas or {}
        )
        self.retriever = Retriever(vector_db=vector_db, data_dir=data_dir)
        self.prompt_builder = PromptBuilder()
        self.executor = Executor(enable_code_execution=True)
        
        # Session storage (in production, use Redis or database)
        self.sessions: Dict[str, UserSession] = {}
    
    async def run_query(self, 
                       query: str,
                       session_id: Optional[str] = None,
                       context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a user query through the complete agent pipeline.
        
        Args:
            query: User query string
            session_id: Optional session ID for conversation continuity
            context: Optional additional context
            
        Returns:
            AgentResponse with processed results
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Get or create user session
            session = self._get_or_create_session(session_id)
            session.start_new_turn(query)
            
            # Step 2: Intent Classification
            print("🎯 Classifying intent...")
            intent_result = self.intent_classifier.classify_intent(
                query, 
                context=session.get_file_context_summary()
            )
            
            # Step 3: Entity Extraction
            print("🔍 Extracting entities...")
            entity_result = self.entity_extractor.extract_entities(
                query,
                context={
                    "available_files": self.clarifier.available_files,
                    "available_columns": self._get_available_columns()
                }
            )
            
            # Combine entities from both sources
            combined_entities = {**intent_result.entities, **entity_result.structured_entities}
            
            # Step 4: Clarification Check
            print("❓ Checking for clarification needs...")
            clarification_result = self.clarifier.check_clarification_needed(
                query=query,
                intent=intent_result.primary_intent,
                entities=combined_entities,
                session=session
            )
            
            # If clarification is needed, return clarification response
            if clarification_result.status == ClarificationStatus.CLARIFICATION_NEEDED:
                session.complete_turn(
                    intent=intent_result.primary_intent.value,
                    entities=combined_entities,
                    ai_response=clarification_result.question,
                    clarification_needed=True,
                    clarification_question=clarification_result.question
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AgentResponse(
                    message=clarification_result.question,
                    intent=intent_result.primary_intent.value,
                    entities=combined_entities,
                    clarification_needed=True,
                    follow_up_suggestions=clarification_result.suggestions,
                    confidence=clarification_result.confidence,
                    processing_time=processing_time
                )
            
            # Step 5: Data Retrieval
            print("📊 Retrieving relevant data...")
            retrieval_result = self.retriever.retrieve_context(
                query=query,
                entities=combined_entities,
                max_results=3
            )
            
            # Update session with focused files
            for doc in retrieval_result.documents:
                session.add_file_focus(
                    doc["file_path"],
                    doc["file_name"],
                    doc.get("columns", [])
                )
            
            # Step 6: Prompt Building
            print("📝 Building LLM prompt...")
            prompt = self.prompt_builder.build_prompt(
                query=query,
                intent=intent_result.primary_intent,
                retrieved_context={
                    "documents": retrieval_result.documents,
                    "metadata": retrieval_result.metadata
                },
                session=session,
                entities=combined_entities
            )
            
            # Step 7: LLM Processing
            print("🤖 Processing with LLM...")
            llm_response = await self._query_llm(prompt)
            
            # Step 8: Result Execution and Formatting
            print("⚡ Executing and formatting results...")
            formatted_response = self.executor.process_llm_response(
                llm_response=llm_response,
                query=query,
                intent=intent_result.primary_intent.value,
                file_paths=retrieval_result.file_paths
            )
            
            # Complete the conversation turn
            session.complete_turn(
                intent=intent_result.primary_intent.value,
                entities=combined_entities,
                ai_response=formatted_response.message,
                code_generated=formatted_response.code,
                execution_result=formatted_response.execution_result
            )
            
            # Calculate processing time and confidence
            processing_time = (datetime.now() - start_time).total_seconds()
            overall_confidence = self._calculate_overall_confidence(
                intent_result.confidence,
                entity_result.confidence,
                retrieval_result.confidence
            )
            
            return AgentResponse(
                message=formatted_response.message,
                code=formatted_response.code,
                execution_result=formatted_response.execution_result,
                code_type=formatted_response.code_type,
                attachments=formatted_response.attachments,
                follow_up_suggestions=formatted_response.follow_up_suggestions,
                intent=intent_result.primary_intent.value,
                entities=combined_entities,
                clarification_needed=False,
                confidence=overall_confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"❌ Error in agent pipeline: {e}")
            
            # Create error response
            error_response = self.executor.format_error_response(str(e), query)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                message=error_response.message,
                follow_up_suggestions=error_response.follow_up_suggestions,
                intent="error",
                confidence=0.0,
                processing_time=processing_time
            )
    
    def _get_or_create_session(self, session_id: Optional[str]) -> UserSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        session = UserSession(session_id=session_id)
        self.sessions[session.session_id] = session
        return session
    
    def _get_available_columns(self) -> List[str]:
        """Get all available columns from file schemas."""
        all_columns = set()
        for columns in self.clarifier.file_schemas.values():
            all_columns.update(columns)
        return list(all_columns)
    
    async def _query_llm(self, prompt: Dict[str, str]) -> str:
        """Query the LLM with the built prompt."""
        try:
            messages = [
                SystemMessage(content=prompt["system_prompt"]),
                HumanMessage(content=prompt["user_prompt"])
            ]
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.llm.invoke(messages)
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error querying LLM: {e}")
            return f"I encountered an error while processing your request: {e}"
    
    def _calculate_overall_confidence(self, 
                                    intent_confidence: float,
                                    entity_confidence: float,
                                    retrieval_confidence: float) -> float:
        """Calculate overall confidence score."""
        # Weighted average of component confidences
        weights = [0.3, 0.3, 0.4]  # Intent, Entity, Retrieval
        confidences = [intent_confidence, entity_confidence, retrieval_confidence]
        
        weighted_sum = sum(w * c for w, c in zip(weights, confidences))
        return min(1.0, weighted_sum)
    
    def update_available_files(self, files: List[str]):
        """Update available files in all components."""
        self.clarifier.update_available_files(files)
    
    def update_file_schemas(self, schemas: Dict[str, List[str]]):
        """Update file schemas in all components."""
        self.clarifier.update_file_schemas(schemas)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None
    
    def clear_session(self, session_id: str):
        """Clear a specific session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def list_active_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self.sessions.keys()) 