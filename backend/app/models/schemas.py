from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, date
from enum import Enum
from uuid import UUID


# Search schemas
class SearchResult(BaseModel):
    type: Literal["claim", "customer", "run"]
    id: str
    title: str
    subtitle: str


class SearchResponse(BaseModel):
    results: List["SearchResult"]
    total: int


# Enums
class TriageLabel(str, Enum):
    STP = "STP"
    REVIEW = "REVIEW"
    HIGH_RISK = "HIGH_RISK"


class DecisionStatus(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    PENDING = "PENDING"


class ForensicsRisk(str, Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# User schemas
class UserBase(BaseModel):
    email: str
    name: str
    role: str = "adjuster"


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Claim schemas
class ClaimBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    policy_number: str
    claim_type: str
    amount: float
    currency: str = "USD"
    incident_date: date
    incident_location: Optional[str] = None
    description: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    triage_label: Optional[TriageLabel] = None
    fraud_score: Optional[float] = None
    risk_score: Optional[float] = None
    decision_status: Optional[DecisionStatus] = None
    confidence: Optional[float] = None
    fast_lane_eligible: Optional[bool] = None
    last_run_id: Optional[UUID] = None


class Claim(ClaimBase):
    id: UUID
    claim_number: str
    triage_label: TriageLabel = TriageLabel.REVIEW
    fraud_score: float = 0
    risk_score: float = 0
    decision_status: DecisionStatus = DecisionStatus.PENDING
    confidence: float = 0
    fast_lane_eligible: bool = False
    last_run_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClaimList(BaseModel):
    id: UUID
    claim_number: str
    customer_name: str
    amount: float
    claim_type: str
    triage_label: TriageLabel
    fraud_score: float
    decision_status: DecisionStatus
    updated_at: datetime
    fast_lane_eligible: bool

    class Config:
        from_attributes = True


# Document schemas
class ClaimDocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    storage_path: str


class ClaimDocumentCreate(ClaimDocumentBase):
    claim_id: UUID


class ClaimDocument(ClaimDocumentBase):
    id: UUID
    claim_id: UUID
    forensics_risk: ForensicsRisk = ForensicsRisk.LOW
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocForensicsSignal(BaseModel):
    id: UUID
    document_id: UUID
    signal_type: str
    severity: ForensicsRisk
    description: str
    details: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# Extraction schemas
class ExtractionCreate(BaseModel):
    claim_id: UUID
    run_id: UUID
    extracted_data: Dict[str, Any]
    schema_valid: bool = True
    validation_errors: List[str] = []


class Extraction(ExtractionCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Policy document schemas
class PolicyDocumentBase(BaseModel):
    name: str
    filename: str
    file_type: str
    storage_path: str


class PolicyDocumentCreate(PolicyDocumentBase):
    pass


class PolicyDocument(PolicyDocumentBase):
    id: UUID
    indexed: bool = False
    chunk_count: int = 0
    uploaded_at: datetime
    indexed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PolicyChunk(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    page_number: Optional[int] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


class PolicyMatch(BaseModel):
    chunk_id: str
    document_name: str
    content: str
    relevance_score: float
    page_number: Optional[int] = None
    section: Optional[str] = None


# Risk score schemas
class RiskFactor(BaseModel):
    name: str
    score: float
    weight: float
    description: str


class RiskScoreCreate(BaseModel):
    claim_id: UUID
    run_id: UUID
    overall_score: float
    factors: List[RiskFactor]


class RiskScore(RiskScoreCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Decision schemas
class DecisionCreate(BaseModel):
    claim_id: UUID
    run_id: UUID
    status: DecisionStatus
    confidence: float
    rationale: str
    next_actions: List[str] = []
    auto_approved: bool = False


class Decision(DecisionCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Audit event schemas
class AuditEventCreate(BaseModel):
    claim_id: Optional[UUID] = None
    run_id: Optional[UUID] = None
    event_type: str
    actor: str = "system"
    payload: Dict[str, Any] = {}


class AuditEvent(AuditEventCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Run schemas
class RunCreate(BaseModel):
    claim_id: UUID
    provider: str = "ollama"


class RunUpdate(BaseModel):
    status: Optional[RunStatus] = None
    current_node: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    trace_id: Optional[str] = None
    error_message: Optional[str] = None


class Run(BaseModel):
    id: UUID
    claim_id: UUID
    status: RunStatus = RunStatus.PENDING
    current_node: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    provider: str = "ollama"
    trace_id: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# Fraud scenario schemas
class FraudScenarioBase(BaseModel):
    name: str
    category: str
    description: str
    threshold: float = 0.5
    enabled: bool = True


class FraudScenarioUpdate(BaseModel):
    threshold: Optional[float] = None
    enabled: Optional[bool] = None


class FraudScenario(FraudScenarioBase):
    id: UUID
    hits_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class FraudHitCreate(BaseModel):
    claim_id: UUID
    run_id: UUID
    scenario_id: UUID
    score: float
    explanation: str


class FraudHit(FraudHitCreate):
    id: UUID
    scenario_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Fast lane override schemas
class FastLaneOverrideCreate(BaseModel):
    claim_id: UUID
    reason: str
    overridden_by: str


class FastLaneOverride(FastLaneOverrideCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Conversation schemas
class ConversationMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    extracted_data: Optional[Dict[str, Any]] = None


class ConversationTranscript(BaseModel):
    id: UUID
    claim_id: Optional[UUID] = None
    messages: List[ConversationMessage] = []
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API Response schemas
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class RunPipelineResponse(BaseModel):
    run_id: UUID
    status: RunStatus
    message: str


class KnowledgeTestResponse(BaseModel):
    query: str
    results: List[PolicyMatch]
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: bool
    database_error: Optional[str] = None
    vector_store: bool
    llm_provider: str
    mode: str = "heuristic"  # "openai", "ollama", or "heuristic"
    heuristic_mode: bool = False


class MetricsResponse(BaseModel):
    claims_today: int
    stp_rate: float
    fraud_hit_rate: float
    avg_decision_time_ms: float
    decision_mix: Dict[str, int]
    top_fraud_scenarios: List[Dict[str, Any]]
    top_policy_exclusions: List[Dict[str, Any]]


# Pipeline state schemas
class PipelineState(BaseModel):
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


# LLM Output schemas for validation
class ExtractedClaimFields(BaseModel):
    provider_name: Optional[str] = None
    service_date: Optional[str] = None
    service_type: Optional[str] = None
    amount: Optional[float] = None
    patient_name: Optional[str] = None
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    additional_info: Dict[str, Any] = {}


class RiskAssessment(BaseModel):
    overall_score: float = Field(ge=0, le=1)
    factors: List[RiskFactor]
    summary: str


class FraudAssessment(BaseModel):
    overall_score: float = Field(ge=0, le=1)
    triggered_scenarios: List[str] = []
    explanations: Dict[str, str] = {}


class DecisionOutput(BaseModel):
    status: DecisionStatus
    confidence: float = Field(ge=0, le=1)
    rationale: str
    next_actions: List[str] = []
