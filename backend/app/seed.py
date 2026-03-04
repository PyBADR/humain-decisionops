"""Database seeding module for HUMAIN DecisionOps.

Run with: python -m app.seed
Or set SEED_ON_STARTUP=true environment variable.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import get_settings
import structlog

logger = structlog.get_logger()

# Seed SQL - Creates tables and inserts demo data
SEED_SQL = """
-- Create tables if not exist
CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_id VARCHAR(50),
    policy_number VARCHAR(50),
    claim_type VARCHAR(100),
    amount DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    incident_date DATE,
    incident_location VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'PENDING',
    triage_label VARCHAR(50) DEFAULT 'REVIEW',
    fast_lane_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES claims(id),
    run_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    confidence DECIMAL(5, 4),
    risk_score DECIMAL(5, 4),
    rationale TEXT,
    next_actions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fraud_scenarios (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    threshold DECIMAL(5, 4) DEFAULT 0.5,
    enabled BOOLEAN DEFAULT TRUE,
    hits_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fraud_hits (
    id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES claims(id),
    scenario_id VARCHAR(50) REFERENCES fraud_scenarios(id),
    score DECIMAL(5, 4),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
    id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50),
    run_id VARCHAR(50),
    event_type VARCHAR(100) NOT NULL,
    node_name VARCHAR(100),
    payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES claims(id),
    status VARCHAR(50) DEFAULT 'PENDING',
    provider VARCHAR(50),
    trace_id VARCHAR(255),
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS policy_documents (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    content TEXT,
    doc_type VARCHAR(100),
    indexed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doc_forensics_signals (
    id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES claims(id),
    document_id VARCHAR(50),
    signal_type VARCHAR(100),
    risk_level VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clear existing demo data
DELETE FROM fraud_hits WHERE claim_id LIKE 'CLM-%';
DELETE FROM audit_events WHERE claim_id LIKE 'CLM-%';
DELETE FROM decisions WHERE claim_id LIKE 'CLM-%';
DELETE FROM runs WHERE claim_id LIKE 'CLM-%';
DELETE FROM doc_forensics_signals WHERE claim_id LIKE 'CLM-%';
DELETE FROM claims WHERE id LIKE 'CLM-%';
DELETE FROM fraud_scenarios WHERE id LIKE 'FS-%';
DELETE FROM policy_documents WHERE id LIKE 'POL-%';

-- Insert demo claims (12 claims)
INSERT INTO claims (id, customer_name, customer_id, policy_number, claim_type, amount, incident_date, incident_location, description, status, triage_label, fast_lane_eligible) VALUES
('CLM-001', 'John Smith', 'CUST-001', 'POL-2024-001', 'Medical Reimbursement', 1250.00, '2024-01-15', 'Seattle, WA', 'Routine checkup and lab work', 'APPROVED', 'STP', true),
('CLM-002', 'Sarah Johnson', 'CUST-002', 'POL-2024-002', 'Auto Collision', 8500.00, '2024-01-18', 'Portland, OR', 'Rear-end collision at intersection', 'PENDING', 'REVIEW', false),
('CLM-003', 'Michael Chen', 'CUST-003', 'POL-2024-003', 'Property Damage', 45000.00, '2024-01-20', 'San Francisco, CA', 'Water damage from burst pipe', 'PENDING', 'HIGH_RISK', false),
('CLM-004', 'Emily Davis', 'CUST-004', 'POL-2024-004', 'Medical Reimbursement', 350.00, '2024-01-22', 'Los Angeles, CA', 'Prescription medication refill', 'APPROVED', 'STP', true),
('CLM-005', 'Robert Wilson', 'CUST-005', 'POL-2024-005', 'Auto Theft', 32000.00, '2024-01-25', 'Denver, CO', 'Vehicle stolen from parking garage', 'PENDING', 'HIGH_RISK', false),
('CLM-006', 'Lisa Anderson', 'CUST-006', 'POL-2024-006', 'Medical Reimbursement', 2100.00, '2024-01-28', 'Austin, TX', 'Emergency room visit', 'PENDING', 'REVIEW', false),
('CLM-007', 'David Martinez', 'CUST-007', 'POL-2024-007', 'Property Damage', 12500.00, '2024-02-01', 'Phoenix, AZ', 'Fire damage to kitchen', 'PENDING', 'REVIEW', false),
('CLM-008', 'Jennifer Taylor', 'CUST-008', 'POL-2024-008', 'Medical Reimbursement', 890.00, '2024-02-03', 'Chicago, IL', 'Physical therapy sessions', 'APPROVED', 'STP', true),
('CLM-009', 'James Brown', 'CUST-009', 'POL-2024-009', 'Auto Collision', 15000.00, '2024-02-05', 'Miami, FL', 'Multi-vehicle accident on highway', 'PENDING', 'HIGH_RISK', false),
('CLM-010', 'Amanda White', 'CUST-010', 'POL-2024-010', 'Medical Reimbursement', 450.00, '2024-02-08', 'Boston, MA', 'Annual dental cleaning', 'APPROVED', 'STP', true),
('CLM-011', 'Christopher Lee', 'CUST-011', 'POL-2024-011', 'Property Damage', 78000.00, '2024-02-10', 'New York, NY', 'Storm damage to roof and siding', 'PENDING', 'HIGH_RISK', false),
('CLM-012', 'Michelle Garcia', 'CUST-012', 'POL-2024-012', 'Auto Collision', 4200.00, '2024-02-12', 'Seattle, WA', 'Minor fender bender in parking lot', 'PENDING', 'REVIEW', false);

-- Insert fraud scenarios (12 scenarios)
INSERT INTO fraud_scenarios (id, name, description, category, threshold, enabled, hits_count) VALUES
('FS-001', 'Excessive Claim Amount', 'Claim amount exceeds 3x policy average', 'Amount', 0.7, true, 5),
('FS-002', 'Duplicate Document Hash', 'Same document submitted for multiple claims', 'Document', 0.9, true, 2),
('FS-003', 'Out-of-Network Provider', 'Service provider not in approved network', 'Provider', 0.5, true, 8),
('FS-004', 'Recent Policy Change', 'Coverage increased within 30 days of claim', 'Policy', 0.6, true, 3),
('FS-005', 'Multiple Claims Short Period', 'More than 3 claims in 90 days', 'Frequency', 0.8, true, 4),
('FS-006', 'Inconsistent Location Data', 'Incident location differs from policy address', 'Location', 0.5, true, 6),
('FS-007', 'Weekend/Holiday Incident', 'Incident occurred on weekend or holiday', 'Timing', 0.3, true, 12),
('FS-008', 'High-Risk Occupation', 'Claimant in high-risk occupation category', 'Profile', 0.4, true, 7),
('FS-009', 'Document Metadata Anomaly', 'PDF creation date after incident date', 'Document', 0.85, true, 1),
('FS-010', 'Velocity Check Failed', 'Claim submitted too quickly after incident', 'Timing', 0.6, true, 3),
('FS-011', 'Known Fraud Ring Association', 'Address or phone linked to known fraud', 'Network', 0.95, true, 0),
('FS-012', 'Template Invoice Detected', 'Invoice matches known fraudulent template', 'Document', 0.9, true, 2);

-- Insert policy documents (2 documents)
INSERT INTO policy_documents (id, name, file_path, content, doc_type, indexed) VALUES
('POL-DOC-001', 'Standard Medical Policy', '/policies/medical_policy.pdf', 'Coverage includes routine checkups, emergency care, prescription medications, and specialist visits. Deductible: $500. Maximum annual benefit: $100,000. Pre-authorization required for procedures over $5,000.', 'medical', true),
('POL-DOC-002', 'Auto Insurance Policy', '/policies/auto_policy.pdf', 'Comprehensive coverage for collision, theft, and liability. Deductible: $1,000. Coverage limit: $50,000 per incident. Rental car coverage included up to $50/day for 30 days.', 'auto', true);

-- Insert sample decisions for approved claims
INSERT INTO decisions (id, claim_id, run_id, status, confidence, risk_score, rationale, next_actions) VALUES
('DEC-001', 'CLM-001', 'RUN-001', 'APPROVE', 0.95, 0.15, 'Low-risk medical reimbursement within policy limits. No fraud signals detected.', '["process_payment", "send_confirmation"]'),
('DEC-004', 'CLM-004', 'RUN-004', 'APPROVE', 0.98, 0.08, 'Routine prescription refill. Amount within normal range.', '["process_payment"]'),
('DEC-008', 'CLM-008', 'RUN-008', 'APPROVE', 0.92, 0.18, 'Physical therapy covered under policy. Provider in network.', '["process_payment", "send_confirmation"]'),
('DEC-010', 'CLM-010', 'RUN-010', 'APPROVE', 0.97, 0.05, 'Routine dental covered. No anomalies detected.', '["process_payment"]');

-- Insert sample audit events
INSERT INTO audit_events (id, claim_id, run_id, event_type, node_name, payload) VALUES
('AUD-001', 'CLM-001', 'RUN-001', 'pipeline_started', 'ingest_document', '{"timestamp": "2024-01-15T10:00:00Z"}'),
('AUD-002', 'CLM-001', 'RUN-001', 'extraction_complete', 'extract_structured_fields', '{"fields_extracted": 12}'),
('AUD-003', 'CLM-001', 'RUN-001', 'decision_made', 'make_decision', '{"decision": "APPROVE", "confidence": 0.95}'),
('AUD-004', 'CLM-003', 'RUN-003', 'fraud_signal_detected', 'fraud_heuristics', '{"scenario": "Excessive Claim Amount", "score": 0.82}'),
('AUD-005', 'CLM-005', 'RUN-005', 'high_risk_flagged', 'compute_risk_signals', '{"risk_score": 0.78, "factors": ["theft", "high_value"]}');

-- Insert sample fraud hits
INSERT INTO fraud_hits (id, claim_id, scenario_id, score, explanation) VALUES
('FH-001', 'CLM-003', 'FS-001', 0.82, 'Claim amount $45,000 exceeds 3x average of $12,000'),
('FH-002', 'CLM-005', 'FS-001', 0.75, 'Vehicle value claim is at policy maximum'),
('FH-003', 'CLM-009', 'FS-005', 0.68, 'Third claim in 60 days for this customer'),
('FH-004', 'CLM-011', 'FS-001', 0.88, 'Claim amount $78,000 significantly above average');

-- Insert sample runs
INSERT INTO runs (id, claim_id, status, provider, duration_ms, created_at, completed_at) VALUES
('RUN-001', 'CLM-001', 'COMPLETED', 'heuristic', 1250, '2024-01-15T10:00:00Z', '2024-01-15T10:00:01Z'),
('RUN-004', 'CLM-004', 'COMPLETED', 'heuristic', 980, '2024-01-22T14:30:00Z', '2024-01-22T14:30:01Z'),
('RUN-008', 'CLM-008', 'COMPLETED', 'heuristic', 1100, '2024-02-03T09:15:00Z', '2024-02-03T09:15:01Z'),
('RUN-010', 'CLM-010', 'COMPLETED', 'heuristic', 850, '2024-02-08T11:45:00Z', '2024-02-08T11:45:01Z');
"""


def run_seed():
    """Execute database seeding."""
    settings = get_settings()
    
    logger.info("seed_starting", database_url=settings.database_url[:30] + "...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Execute seed SQL
            for statement in SEED_SQL.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        
        logger.info("seed_completed", message="Database seeded successfully with 12 claims, 12 fraud scenarios, 2 policy documents")
        return True
        
    except Exception as e:
        logger.error("seed_failed", error=str(e))
        return False


if __name__ == "__main__":
    success = run_seed()
    sys.exit(0 if success else 1)
