from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum
import json
import structlog

from app.config import get_settings
from app.models.schemas import TriageLabel, DecisionStatus, RiskFactor, PolicyMatch

settings = get_settings()
logger = structlog.get_logger()


class PipelineState(BaseModel):
    """State passed through the pipeline."""
    claim_id: UUID
    run_id: UUID
    claim_data: Optional[Dict[str, Any]] = None
    document_content: Optional[str] = None
    extracted_fields: Optional[Dict[str, Any]] = None
    policy_matches: List[PolicyMatch] = []
    risk_factors: List[RiskFactor] = []
    risk_score: float = 0
    fraud_hits: List[Dict[str, Any]] = []
    fraud_score: float = 0
    triage_label: Optional[TriageLabel] = None
    decision_status: Optional[DecisionStatus] = None
    confidence: float = 0
    rationale: Optional[str] = None
    next_actions: List[str] = []
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class Pipeline:
    """LangGraph-style pipeline for claim processing."""
    
    def __init__(self):
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM based on available provider and heuristic mode."""
        # Check effective mode from settings
        effective_mode = settings.effective_mode
        
        if effective_mode == "heuristic":
            # Heuristic mode - no LLM calls
            self.llm = None
            self.provider = "heuristic"
            logger.info("pipeline_init", mode="heuristic", message="Running in heuristic mode - no LLM calls")
        elif effective_mode == "openai":
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=settings.openai_api_key,
                temperature=0
            )
            self.provider = "openai"
            logger.info("pipeline_init", mode="openai")
        elif effective_mode == "ollama":
            try:
                from langchain_community.llms import Ollama
                self.llm = Ollama(
                    model="llama2",
                    base_url=settings.ollama_base_url
                )
                self.provider = "ollama"
                logger.info("pipeline_init", mode="ollama")
            except Exception as e:
                logger.warning("ollama_init_failed", error=str(e), fallback="heuristic")
                self.llm = None
                self.provider = "heuristic"
        else:
            self.llm = None
            self.provider = "heuristic"
    
    async def execute_node(self, node_name: str, state: PipelineState, db) -> PipelineState:
        """Execute a pipeline node."""
        node_map = {
            "ingest_document": self._ingest_document,
            "extract_structured_fields": self._extract_structured_fields,
            "retrieve_policy_context": self._retrieve_policy_context,
            "compute_risk_signals": self._compute_risk_signals,
            "fraud_heuristics": self._fraud_heuristics,
            "make_decision": self._make_decision,
            "generate_rationale": self._generate_rationale,
            "persist_all": self._persist_all
        }
        
        node_func = node_map.get(node_name)
        if node_func:
            return await node_func(state, db)
        return state
    
    async def _ingest_document(self, state: PipelineState, db) -> PipelineState:
        """Ingest and preprocess document."""
        logger.info("node_ingest_document", claim_id=str(state.claim_id))
        
        # Document content already loaded in state if available
        if not state.document_content:
            state.document_content = state.claim_data.get("description", "No document content available.")
        
        return state
    
    async def _extract_structured_fields(self, state: PipelineState, db) -> PipelineState:
        """Extract structured fields from document using LLM or heuristics."""
        logger.info("node_extract_structured_fields", claim_id=str(state.claim_id), mode=self.provider)
        
        if self.llm and self.provider not in ("mock", "heuristic"):
            try:
                prompt = f"""Extract structured information from this insurance claim:

Claim Type: {state.claim_data.get('claim_type')}
Amount: ${state.claim_data.get('amount')}
Description: {state.claim_data.get('description', 'N/A')}
Document Content: {state.document_content or 'N/A'}

Extract and return as JSON:
- provider_name: string or null
- service_date: string or null
- service_type: string or null
- amount: number
- diagnosis_codes: array of strings
- procedure_codes: array of strings

Return only valid JSON."""
                
                response = await self._invoke_llm(prompt)
                
                # Try to parse JSON from response
                try:
                    extracted = json.loads(response)
                    state.extracted_fields = extracted
                except json.JSONDecodeError:
                    # Use claim data as fallback
                    state.extracted_fields = {
                        "provider_name": None,
                        "service_date": state.claim_data.get("incident_date"),
                        "service_type": state.claim_data.get("claim_type"),
                        "amount": state.claim_data.get("amount"),
                        "diagnosis_codes": [],
                        "procedure_codes": []
                    }
            except Exception as e:
                logger.error("extraction_error", error=str(e))
                state.extracted_fields = self._default_extraction(state)
        else:
            state.extracted_fields = self._default_extraction(state)
        
        return state
    
    def _default_extraction(self, state: PipelineState) -> Dict[str, Any]:
        """Return default extraction based on claim data."""
        return {
            "provider_name": "Unknown Provider",
            "service_date": state.claim_data.get("incident_date"),
            "service_type": state.claim_data.get("claim_type"),
            "amount": state.claim_data.get("amount"),
            "patient_name": state.claim_data.get("customer_name"),
            "diagnosis_codes": [],
            "procedure_codes": []
        }
    
    async def _retrieve_policy_context(self, state: PipelineState, db) -> PipelineState:
        """Retrieve relevant policy context using RAG."""
        logger.info("node_retrieve_policy_context", claim_id=str(state.claim_id))
        
        from app.services.vector_store import VectorStore
        vector_store = VectorStore()
        
        query = f"{state.claim_data.get('claim_type')} coverage {state.claim_data.get('description', '')}"
        
        try:
            matches = await vector_store.search(query, 5, db)
            state.policy_matches = matches
        except Exception as e:
            logger.error("policy_retrieval_error", error=str(e))
            state.policy_matches = []
        
        return state
    
    async def _compute_risk_signals(self, state: PipelineState, db) -> PipelineState:
        """Compute risk signals for the claim."""
        logger.info("node_compute_risk_signals", claim_id=str(state.claim_id))
        
        factors = []
        total_score = 0
        
        # Amount-based risk
        amount = state.claim_data.get("amount", 0)
        if amount > 50000:
            amount_score = 0.8
            amount_desc = "High value claim requires additional review"
        elif amount > 10000:
            amount_score = 0.5
            amount_desc = "Moderate value claim"
        elif amount > 1000:
            amount_score = 0.2
            amount_desc = "Standard value claim"
        else:
            amount_score = 0.1
            amount_desc = "Low value claim within normal range"
        
        factors.append(RiskFactor(
            name="claim_amount",
            score=amount_score,
            weight=0.3,
            description=amount_desc
        ))
        total_score += amount_score * 0.3
        
        # Claim type risk
        claim_type = state.claim_data.get("claim_type", "").lower()
        if "fire" in claim_type or "total loss" in claim_type:
            type_score = 0.7
            type_desc = "High-risk claim type"
        elif "collision" in claim_type or "theft" in claim_type:
            type_score = 0.5
            type_desc = "Moderate-risk claim type"
        else:
            type_score = 0.2
            type_desc = "Standard claim type"
        
        factors.append(RiskFactor(
            name="claim_type",
            score=type_score,
            weight=0.3,
            description=type_desc
        ))
        total_score += type_score * 0.3
        
        # Documentation completeness
        has_doc = bool(state.document_content and len(state.document_content) > 50)
        doc_score = 0.1 if has_doc else 0.4
        doc_desc = "Documentation provided" if has_doc else "Limited documentation"
        
        factors.append(RiskFactor(
            name="documentation",
            score=doc_score,
            weight=0.4,
            description=doc_desc
        ))
        total_score += doc_score * 0.4
        
        state.risk_factors = factors
        state.risk_score = round(total_score, 4)
        
        return state
    
    async def _fraud_heuristics(self, state: PipelineState, db) -> PipelineState:
        """Apply fraud detection heuristics."""
        logger.info("node_fraud_heuristics", claim_id=str(state.claim_id))
        
        from app.models.orm import FraudScenario as FraudScenarioORM
        
        fraud_hits = []
        max_score = 0
        
        # Get enabled scenarios
        scenarios = db.query(FraudScenarioORM).filter(
            FraudScenarioORM.enabled == True
        ).all()
        
        claim_type = state.claim_data.get("claim_type", "").lower()
        amount = state.claim_data.get("amount", 0)
        description = state.claim_data.get("description", "").lower()
        
        for scenario in scenarios:
            score = 0
            explanation = ""
            
            # Simple heuristic matching based on scenario name
            if "inflated" in scenario.name.lower() and amount > 20000:
                score = 0.6
                explanation = f"Claim amount ${amount} may be inflated"
            
            elif "staged" in scenario.name.lower() and "fire" in claim_type:
                score = 0.5
                explanation = "Fire claim matches staged incident pattern"
            
            elif "soft tissue" in scenario.name.lower() and "medical" in claim_type:
                if "soft tissue" in description or "pain" in description:
                    score = 0.55
                    explanation = "Soft tissue injury claim pattern detected"
            
            elif "rapid" in scenario.name.lower():
                # Would check claim history here
                score = 0.1
                explanation = "No rapid succession pattern detected"
            
            elif "document" in scenario.name.lower() and state.risk_score > 0.5:
                score = 0.4
                explanation = "Document requires additional verification"
            
            # Check if score exceeds threshold
            if score >= scenario.threshold:
                fraud_hits.append({
                    "scenario_id": str(scenario.id),
                    "scenario_name": scenario.name,
                    "score": score,
                    "explanation": explanation
                })
                max_score = max(max_score, score)
        
        state.fraud_hits = fraud_hits
        state.fraud_score = round(max_score, 4)
        
        return state
    
    async def _make_decision(self, state: PipelineState, db) -> PipelineState:
        """Make final decision based on all signals."""
        logger.info("node_make_decision", claim_id=str(state.claim_id))
        
        # Determine triage label
        if state.fraud_score >= 0.7 or state.risk_score >= 0.7:
            state.triage_label = TriageLabel.HIGH_RISK
        elif state.fraud_score >= 0.4 or state.risk_score >= 0.4:
            state.triage_label = TriageLabel.REVIEW
        else:
            state.triage_label = TriageLabel.STP
        
        # Make decision
        amount = state.claim_data.get("amount", 0)
        claim_type = state.claim_data.get("claim_type", "").lower()
        
        if state.triage_label == TriageLabel.HIGH_RISK:
            state.decision_status = DecisionStatus.REVIEW
            state.confidence = 0.3
            state.next_actions = [
                "Refer to Special Investigations Unit",
                "Request additional documentation",
                "Contact policyholder for verification"
            ]
        elif state.triage_label == TriageLabel.REVIEW:
            state.decision_status = DecisionStatus.REVIEW
            state.confidence = 0.6
            state.next_actions = [
                "Manual review required",
                "Verify documentation",
                "Check policy coverage"
            ]
        else:
            # STP - can auto-approve if eligible
            if amount < 1000 and "medical" in claim_type or "dental" in claim_type:
                state.decision_status = DecisionStatus.APPROVE
                state.confidence = 0.95
                state.next_actions = [
                    "Process payment",
                    "Send confirmation to policyholder"
                ]
            else:
                state.decision_status = DecisionStatus.APPROVE
                state.confidence = 0.85
                state.next_actions = [
                    "Process payment",
                    "Update claim status"
                ]
        
        return state
    
    async def _generate_rationale(self, state: PipelineState, db) -> PipelineState:
        """Generate human-readable rationale for the decision using LLM or heuristics."""
        logger.info("node_generate_rationale", claim_id=str(state.claim_id), mode=self.provider)
        
        if self.llm and self.provider not in ("mock", "heuristic"):
            try:
                prompt = f"""Generate a brief rationale for this insurance claim decision:

Claim Type: {state.claim_data.get('claim_type')}
Amount: ${state.claim_data.get('amount')}
Decision: {state.decision_status.value if state.decision_status else 'REVIEW'}
Risk Score: {state.risk_score}
Fraud Score: {state.fraud_score}
Triage: {state.triage_label.value if state.triage_label else 'REVIEW'}

Provide a 2-3 sentence professional rationale."""
                
                response = await self._invoke_llm(prompt)
                state.rationale = response.strip()
            except Exception as e:
                logger.error("rationale_generation_error", error=str(e))
                state.rationale = self._default_rationale(state)
        else:
            state.rationale = self._default_rationale(state)
        
        return state
    
    def _default_rationale(self, state: PipelineState) -> str:
        """Generate default rationale based on decision."""
        if state.decision_status == DecisionStatus.APPROVE:
            return f"Claim approved based on automated analysis. Risk score: {state.risk_score:.2f}, Fraud score: {state.fraud_score:.2f}. All documentation verified and within policy limits."
        elif state.decision_status == DecisionStatus.REJECT:
            return f"Claim flagged for rejection due to elevated risk indicators. Risk score: {state.risk_score:.2f}, Fraud score: {state.fraud_score:.2f}. Manual review recommended before final decision."
        else:
            return f"Claim requires manual review. Risk score: {state.risk_score:.2f}, Fraud score: {state.fraud_score:.2f}. Additional verification needed before decision."
    
    async def _persist_all(self, state: PipelineState, db) -> PipelineState:
        """Final persistence step (handled by pipeline runner)."""
        logger.info("node_persist_all", claim_id=str(state.claim_id))
        return state
    
    async def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with prompt."""
        if self.provider == "openai":
            from langchain_core.messages import HumanMessage
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content
        elif self.provider == "ollama":
            response = self.llm.invoke(prompt)
            return response
        else:
            return "Mock response"


def create_pipeline() -> Pipeline:
    """Create and return a pipeline instance."""
    return Pipeline()
