from sqlalchemy import Column, String, Float, Boolean, Integer, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="adjuster")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255))
    policy_number = Column(String(100), nullable=False)
    claim_type = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    incident_date = Column(Date, nullable=False)
    incident_location = Column(String(500))
    description = Column(Text)
    triage_label = Column(String(20), default="REVIEW")
    fraud_score = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    decision_status = Column(String(20), default="PENDING")
    confidence = Column(Float, default=0)
    fast_lane_eligible = Column(Boolean, default=False)
    last_run_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="claim", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="claim", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="claim", cascade="all, delete-orphan")
    fraud_hits = relationship("FraudHit", back_populates="claim", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="claim", cascade="all, delete-orphan")
    overrides = relationship("FastLaneOverride", back_populates="claim", cascade="all, delete-orphan")


class ClaimDocument(Base):
    __tablename__ = "claim_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    forensics_risk = Column(String(10), default="LOW")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="documents")
    forensics_signals = relationship("DocForensicsSignal", back_populates="document", cascade="all, delete-orphan")


class DocForensicsSignal(Base):
    __tablename__ = "doc_forensics_signals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("claim_documents.id", ondelete="CASCADE"), nullable=False)
    signal_type = Column(String(100), nullable=False)
    severity = Column(String(10), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("ClaimDocument", back_populates="forensics_signals")


class Extraction(Base):
    __tablename__ = "extractions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    extracted_data = Column(JSONB, default={})
    schema_valid = Column(Boolean, default=True)
    validation_errors = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="extractions")


class PolicyDocument(Base):
    __tablename__ = "policy_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    storage_path = Column(String(500), nullable=False)
    indexed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    indexed_at = Column(DateTime(timezone=True))
    
    chunks = relationship("PolicyChunk", back_populates="document", cascade="all, delete-orphan")


class PolicyChunk(Base):
    __tablename__ = "policy_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    section = Column(String(255))
    # embedding column handled separately for pgvector
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("PolicyDocument", back_populates="chunks")


class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    overall_score = Column(Float, nullable=False)
    factors = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="risk_scores")


class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    rationale = Column(Text, nullable=False)
    next_actions = Column(JSONB, default=[])
    auto_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="decisions")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="SET NULL"))
    run_id = Column(UUID(as_uuid=True))
    event_type = Column(String(100), nullable=False)
    actor = Column(String(255), nullable=False, default="system")
    payload = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Run(Base):
    __tablename__ = "runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    current_node = Column(String(100))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    provider = Column(String(50), default="ollama")
    trace_id = Column(String(255))
    error_message = Column(Text)
    
    claim = relationship("Claim", back_populates="runs")


class FraudScenario(Base):
    __tablename__ = "fraud_scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    threshold = Column(Float, default=0.5)
    enabled = Column(Boolean, default=True)
    hits_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    hits = relationship("FraudHit", back_populates="scenario")


class FraudHit(Base):
    __tablename__ = "fraud_hits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("fraud_scenarios.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="fraud_hits")
    scenario = relationship("FraudScenario", back_populates="hits")


class FastLaneOverride(Base):
    __tablename__ = "fast_lane_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    overridden_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    claim = relationship("Claim", back_populates="overrides")


class ConversationTranscript(Base):
    __tablename__ = "conversation_transcripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="SET NULL"))
    messages = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
