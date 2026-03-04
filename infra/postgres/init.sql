-- Humain DecisionOps Database Schema
-- PostgreSQL 16 with pgvector extension

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table (RBAC-lite)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'adjuster' CHECK (role IN ('admin', 'adjuster', 'reviewer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Claims table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    policy_number VARCHAR(100) NOT NULL,
    claim_type VARCHAR(100) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    incident_date DATE NOT NULL,
    incident_location VARCHAR(500),
    description TEXT,
    triage_label VARCHAR(20) DEFAULT 'REVIEW' CHECK (triage_label IN ('STP', 'REVIEW', 'HIGH_RISK')),
    fraud_score DECIMAL(5, 4) DEFAULT 0,
    risk_score DECIMAL(5, 4) DEFAULT 0,
    decision_status VARCHAR(20) DEFAULT 'PENDING' CHECK (decision_status IN ('APPROVE', 'REVIEW', 'REJECT', 'PENDING')),
    confidence DECIMAL(5, 4) DEFAULT 0,
    fast_lane_eligible BOOLEAN DEFAULT FALSE,
    last_run_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Claim documents table
CREATE TABLE claim_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    forensics_risk VARCHAR(10) DEFAULT 'LOW' CHECK (forensics_risk IN ('LOW', 'MED', 'HIGH')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document forensics signals
CREATE TABLE doc_forensics_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES claim_documents(id) ON DELETE CASCADE,
    signal_type VARCHAR(100) NOT NULL,
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('LOW', 'MED', 'HIGH')),
    description TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Extractions table
CREATE TABLE extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    run_id UUID NOT NULL,
    extracted_data JSONB NOT NULL DEFAULT '{}',
    schema_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Policy documents table
CREATE TABLE policy_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    indexed BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    indexed_at TIMESTAMP WITH TIME ZONE
);

-- Policy chunks for vector search
CREATE TABLE policy_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES policy_documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    page_number INTEGER,
    section VARCHAR(255),
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX ON policy_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Risk scores table
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    run_id UUID NOT NULL,
    overall_score DECIMAL(5, 4) NOT NULL,
    factors JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Decisions table
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    run_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('APPROVE', 'REVIEW', 'REJECT')),
    confidence DECIMAL(5, 4) NOT NULL,
    rationale TEXT NOT NULL,
    next_actions JSONB DEFAULT '[]',
    auto_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit events table
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES claims(id) ON DELETE SET NULL,
    run_id UUID,
    event_type VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL DEFAULT 'system',
    payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pipeline runs table
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    current_node VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    provider VARCHAR(50) DEFAULT 'ollama',
    trace_id VARCHAR(255),
    error_message TEXT
);

-- Fraud scenarios table
CREATE TABLE fraud_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    threshold DECIMAL(5, 4) DEFAULT 0.5,
    enabled BOOLEAN DEFAULT TRUE,
    hits_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fraud hits table
CREATE TABLE fraud_hits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    run_id UUID NOT NULL,
    scenario_id UUID NOT NULL REFERENCES fraud_scenarios(id) ON DELETE CASCADE,
    score DECIMAL(5, 4) NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fast lane overrides table
CREATE TABLE fast_lane_overrides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    overridden_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation transcripts table
CREATE TABLE conversation_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES claims(id) ON DELETE SET NULL,
    messages JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_claims_triage ON claims(triage_label);
CREATE INDEX idx_claims_status ON claims(decision_status);
CREATE INDEX idx_claims_fast_lane ON claims(fast_lane_eligible);
CREATE INDEX idx_claims_created ON claims(created_at DESC);
CREATE INDEX idx_audit_events_claim ON audit_events(claim_id);
CREATE INDEX idx_audit_events_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_created ON audit_events(created_at DESC);
CREATE INDEX idx_runs_claim ON runs(claim_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_fraud_hits_claim ON fraud_hits(claim_id);
CREATE INDEX idx_extractions_claim ON extractions(claim_id);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_claims_updated_at
    BEFORE UPDATE ON claims
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
