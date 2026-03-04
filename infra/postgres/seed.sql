-- Humain DecisionOps Seed Data

-- Insert demo users
INSERT INTO users (id, email, name, role) VALUES
('11111111-1111-1111-1111-111111111111', 'admin@humain.ai', 'Admin User', 'admin'),
('22222222-2222-2222-2222-222222222222', 'adjuster@humain.ai', 'John Adjuster', 'adjuster'),
('33333333-3333-3333-3333-333333333333', 'reviewer@humain.ai', 'Jane Reviewer', 'reviewer');

-- Insert 12 fraud scenarios
INSERT INTO fraud_scenarios (id, name, category, description, threshold, enabled, hits_count) VALUES
('f0000001-0000-0000-0000-000000000001', 'Duplicate Claim Submission', 'Identity', 'Same incident reported multiple times with slight variations', 0.7, true, 3),
('f0000002-0000-0000-0000-000000000002', 'Inflated Repair Costs', 'Financial', 'Repair estimates significantly above market rates', 0.6, true, 5),
('f0000003-0000-0000-0000-000000000003', 'Staged Accident Pattern', 'Collision', 'Indicators of pre-arranged vehicle collision', 0.8, true, 2),
('f0000004-0000-0000-0000-000000000004', 'Ghost Vendor Invoice', 'Vendor', 'Invoice from non-existent or suspicious vendor', 0.75, true, 4),
('f0000005-0000-0000-0000-000000000005', 'Medical Provider Mill', 'Medical', 'Claims routed through known problematic medical providers', 0.65, true, 6),
('f0000006-0000-0000-0000-000000000006', 'Rapid Succession Claims', 'Timing', 'Multiple claims filed in unusually short timeframe', 0.55, true, 3),
('f0000007-0000-0000-0000-000000000007', 'Address Inconsistency', 'Identity', 'Mismatch between policy address and claim location', 0.5, true, 2),
('f0000008-0000-0000-0000-000000000008', 'Late Night Incident', 'Timing', 'Incident reported during unusual hours with no witnesses', 0.45, true, 1),
('f0000009-0000-0000-0000-000000000009', 'Premium Jump Before Claim', 'Policy', 'Coverage increased shortly before incident', 0.7, true, 2),
('f0000010-0000-0000-0000-000000000010', 'Document Tampering', 'Document', 'Signs of digital manipulation in submitted documents', 0.85, true, 3),
('f0000011-0000-0000-0000-000000000011', 'Network Ring Association', 'Network', 'Claimant connected to known fraud ring members', 0.9, true, 1),
('f0000012-0000-0000-0000-000000000012', 'Soft Tissue Only', 'Medical', 'Claims exclusively for hard-to-verify soft tissue injuries', 0.4, true, 8);

-- Insert 10+ demo claims with varied statuses
INSERT INTO claims (id, claim_number, customer_name, customer_email, policy_number, claim_type, amount, currency, incident_date, incident_location, description, triage_label, fraud_score, risk_score, decision_status, confidence, fast_lane_eligible) VALUES
-- STP Claims (2 fast-lane eligible)
('c0000001-0000-0000-0000-000000000001', 'CLM-2024-001', 'Sarah Johnson', 'sarah.j@email.com', 'POL-MED-10001', 'Medical Reimbursement', 450.00, 'USD', '2024-01-15', 'Austin, TX', 'Routine dental checkup and cleaning reimbursement request', 'STP', 0.05, 0.10, 'APPROVE', 0.95, true),
('c0000002-0000-0000-0000-000000000002', 'CLM-2024-002', 'Michael Chen', 'mchen@email.com', 'POL-MED-10002', 'Medical Reimbursement', 275.00, 'USD', '2024-01-18', 'Seattle, WA', 'Annual physical examination copay reimbursement', 'STP', 0.03, 0.08, 'APPROVE', 0.97, true),
('c0000003-0000-0000-0000-000000000003', 'CLM-2024-003', 'Emily Rodriguez', 'erodriguez@email.com', 'POL-AUTO-20001', 'Auto - Minor Damage', 1200.00, 'USD', '2024-01-20', 'Phoenix, AZ', 'Minor fender bender in parking lot, photos attached', 'STP', 0.08, 0.15, 'APPROVE', 0.92, false),

-- REVIEW Claims
('c0000004-0000-0000-0000-000000000004', 'CLM-2024-004', 'David Thompson', 'dthompson@email.com', 'POL-HOME-30001', 'Property - Water Damage', 8500.00, 'USD', '2024-01-22', 'Denver, CO', 'Basement flooding due to pipe burst during cold snap', 'REVIEW', 0.25, 0.45, 'REVIEW', 0.65, false),
('c0000005-0000-0000-0000-000000000005', 'CLM-2024-005', 'Jennifer Martinez', 'jmartinez@email.com', 'POL-AUTO-20002', 'Auto - Collision', 15000.00, 'USD', '2024-01-25', 'Los Angeles, CA', 'Multi-vehicle accident on highway, significant damage', 'REVIEW', 0.35, 0.55, 'PENDING', 0.55, false),
('c0000006-0000-0000-0000-000000000006', 'CLM-2024-006', 'Robert Wilson', 'rwilson@email.com', 'POL-MED-10003', 'Medical - Surgery', 25000.00, 'USD', '2024-01-28', 'Chicago, IL', 'Knee replacement surgery claim with extended rehab', 'REVIEW', 0.20, 0.40, 'PENDING', 0.70, false),
('c0000007-0000-0000-0000-000000000007', 'CLM-2024-007', 'Amanda Lee', 'alee@email.com', 'POL-HOME-30002', 'Property - Theft', 5500.00, 'USD', '2024-02-01', 'Miami, FL', 'Home burglary while on vacation, electronics stolen', 'REVIEW', 0.40, 0.50, 'PENDING', 0.60, false),

-- HIGH_RISK Claims (with fraud hits)
('c0000008-0000-0000-0000-000000000008', 'CLM-2024-008', 'James Brown', 'jbrown@email.com', 'POL-AUTO-20003', 'Auto - Total Loss', 45000.00, 'USD', '2024-02-05', 'Las Vegas, NV', 'Vehicle fire in remote location, total loss claimed', 'HIGH_RISK', 0.78, 0.85, 'REVIEW', 0.30, false),
('c0000009-0000-0000-0000-000000000009', 'CLM-2024-009', 'Patricia Davis', 'pdavis@email.com', 'POL-MED-10004', 'Medical - Multiple Treatments', 35000.00, 'USD', '2024-02-08', 'Houston, TX', 'Extensive soft tissue treatment from minor accident', 'HIGH_RISK', 0.82, 0.80, 'REJECT', 0.25, false),
('c0000010-0000-0000-0000-000000000010', 'CLM-2024-010', 'Christopher Garcia', 'cgarcia@email.com', 'POL-HOME-30003', 'Property - Fire', 120000.00, 'USD', '2024-02-10', 'Atlanta, GA', 'House fire with suspicious origin, high value items claimed', 'HIGH_RISK', 0.88, 0.90, 'PENDING', 0.20, false),

-- Additional claims for variety
('c0000011-0000-0000-0000-000000000011', 'CLM-2024-011', 'Lisa Anderson', 'landerson@email.com', 'POL-AUTO-20004', 'Auto - Windshield', 350.00, 'USD', '2024-02-12', 'Portland, OR', 'Windshield crack from road debris', 'STP', 0.02, 0.05, 'APPROVE', 0.98, true),
('c0000012-0000-0000-0000-000000000012', 'CLM-2024-012', 'Kevin White', 'kwhite@email.com', 'POL-MED-10005', 'Medical - Emergency', 8900.00, 'USD', '2024-02-15', 'Boston, MA', 'Emergency room visit for chest pain, cardiac workup', 'REVIEW', 0.15, 0.30, 'PENDING', 0.75, false);

-- Insert claim documents
INSERT INTO claim_documents (id, claim_id, filename, file_type, file_size, storage_path, forensics_risk) VALUES
('d0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', 'dental_receipt.pdf', 'application/pdf', 125000, '/uploads/c0000001/dental_receipt.pdf', 'LOW'),
('d0000002-0000-0000-0000-000000000002', 'c0000003-0000-0000-0000-000000000003', 'accident_photos.pdf', 'application/pdf', 2500000, '/uploads/c0000003/accident_photos.pdf', 'LOW'),
('d0000003-0000-0000-0000-000000000003', 'c0000004-0000-0000-0000-000000000004', 'water_damage_assessment.pdf', 'application/pdf', 1800000, '/uploads/c0000004/water_damage_assessment.pdf', 'MED'),
('d0000004-0000-0000-0000-000000000004', 'c0000008-0000-0000-0000-000000000008', 'fire_report.pdf', 'application/pdf', 950000, '/uploads/c0000008/fire_report.pdf', 'HIGH'),
('d0000005-0000-0000-0000-000000000005', 'c0000009-0000-0000-0000-000000000009', 'medical_records.pdf', 'application/pdf', 3200000, '/uploads/c0000009/medical_records.pdf', 'HIGH'),
('d0000006-0000-0000-0000-000000000006', 'c0000010-0000-0000-0000-000000000010', 'fire_investigation.pdf', 'application/pdf', 4500000, '/uploads/c0000010/fire_investigation.pdf', 'HIGH');

-- Insert document forensics signals for HIGH_RISK claims
INSERT INTO doc_forensics_signals (id, document_id, signal_type, severity, description, details) VALUES
('e5000001-0000-0000-0000-000000000001', 'd0000004-0000-0000-0000-000000000004', 'metadata_anomaly', 'HIGH', 'PDF creation date inconsistent with incident date', '{"creation_date": "2024-01-15", "incident_date": "2024-02-05", "software": "Unknown PDF Editor"}'),
('e5000002-0000-0000-0000-000000000002', 'd0000004-0000-0000-0000-000000000004', 'template_match', 'MED', 'Document matches known fraudulent template pattern', '{"template_id": "TPL-FIRE-003", "similarity": 0.87}'),
('e5000003-0000-0000-0000-000000000003', 'd0000005-0000-0000-0000-000000000005', 'vendor_mismatch', 'HIGH', 'Medical provider not found in verified database', '{"provider_name": "QuickHeal Medical Center", "npi_valid": false}'),
('e5000004-0000-0000-0000-000000000004', 'd0000005-0000-0000-0000-000000000005', 'excessive_billing', 'MED', 'Billing codes exceed typical treatment patterns', '{"codes": ["99215", "97140", "97110"], "frequency": "daily", "duration_weeks": 12}'),
('e5000005-0000-0000-0000-000000000005', 'd0000006-0000-0000-0000-000000000006', 'image_manipulation', 'HIGH', 'Signs of digital editing detected in damage photos', '{"tool": "Photoshop", "edit_regions": 3, "confidence": 0.92}');

-- Insert fraud hits for HIGH_RISK claims
INSERT INTO fraud_hits (id, claim_id, run_id, scenario_id, score, explanation) VALUES
('a0000001-0000-0000-0000-000000000001', 'c0000008-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000000', 'f0000003-0000-0000-0000-000000000003', 0.75, 'Vehicle fire in remote location with no witnesses matches staged accident pattern'),
('a0000002-0000-0000-0000-000000000002', 'c0000008-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000000', 'f0000010-0000-0000-0000-000000000010', 0.87, 'Document metadata shows signs of tampering'),
('a0000003-0000-0000-0000-000000000003', 'c0000009-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000000', 'f0000005-0000-0000-0000-000000000005', 0.82, 'Medical provider flagged in fraud database'),
('a0000004-0000-0000-0000-000000000004', 'c0000009-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000000', 'f0000012-0000-0000-0000-000000000012', 0.78, 'Claim exclusively for soft tissue injuries with extended treatment'),
('a0000005-0000-0000-0000-000000000005', 'c0000010-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000000', 'f0000009-0000-0000-0000-000000000009', 0.85, 'Coverage increased 30 days before fire incident'),
('a0000006-0000-0000-0000-000000000006', 'c0000010-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000000', 'f0000010-0000-0000-0000-000000000010', 0.92, 'Multiple images show evidence of digital manipulation');

-- Insert policy documents
INSERT INTO policy_documents (id, name, filename, file_type, storage_path, indexed, chunk_count) VALUES
('b0000001-0000-0000-0000-000000000001', 'Auto Insurance Policy Guide', 'auto_policy_guide.pdf', 'application/pdf', '/policies/auto_policy_guide.pdf', true, 45),
('b0000002-0000-0000-0000-000000000002', 'Medical Coverage Handbook', 'medical_coverage_handbook.pdf', 'application/pdf', '/policies/medical_coverage_handbook.pdf', true, 62);

-- Insert sample audit events
INSERT INTO audit_events (id, claim_id, run_id, event_type, actor, payload) VALUES
('ae000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', NULL, 'claim_created', 'system', '{"source": "web_portal", "ip": "192.168.1.100"}'),
('ae000002-0000-0000-0000-000000000002', 'c0000001-0000-0000-0000-000000000001', NULL, 'document_uploaded', 'system', '{"filename": "dental_receipt.pdf", "size": 125000}'),
('ae000003-0000-0000-0000-000000000003', 'c0000001-0000-0000-0000-000000000001', NULL, 'pipeline_started', 'system', '{"provider": "ollama"}'),
('ae000004-0000-0000-0000-000000000004', 'c0000001-0000-0000-0000-000000000001', NULL, 'triage_assigned', 'pipeline', '{"label": "STP", "confidence": 0.95}'),
('ae000005-0000-0000-0000-000000000005', 'c0000001-0000-0000-0000-000000000001', NULL, 'decision_made', 'pipeline', '{"status": "APPROVE", "auto_approved": true}'),
('ae000006-0000-0000-0000-000000000006', 'c0000008-0000-0000-0000-000000000008', NULL, 'fraud_alert', 'pipeline', '{"scenarios": ["Staged Accident Pattern", "Document Tampering"], "score": 0.78}'),
('ae000007-0000-0000-0000-000000000007', 'c0000009-0000-0000-0000-000000000009', NULL, 'decision_made', 'pipeline', '{"status": "REJECT", "reason": "Multiple fraud indicators detected"}');

-- Insert sample extractions
INSERT INTO extractions (id, claim_id, run_id, extracted_data, schema_valid) VALUES
('e0000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', '{"provider_name": "Austin Dental Care", "service_date": "2024-01-15", "service_type": "Preventive - Cleaning", "amount": 450.00, "patient_name": "Sarah Johnson"}', true),
('e0000002-0000-0000-0000-000000000002', 'c0000003-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000000', '{"incident_type": "Parking Lot Collision", "damage_location": "Rear Bumper", "estimated_repair": 1200.00, "other_party": "None - Single Vehicle"}', true);

-- Insert sample decisions
INSERT INTO decisions (id, claim_id, run_id, status, confidence, rationale, next_actions, auto_approved) VALUES
('de000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 'APPROVE', 0.95, 'Routine dental claim with valid documentation. Amount within policy limits. No fraud indicators detected. Provider verified in network.', '["Process payment", "Send confirmation to policyholder"]', true),
('de000002-0000-0000-0000-000000000002', 'c0000002-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000000', 'APPROVE', 0.97, 'Standard annual physical reimbursement. All documentation complete. Provider in-network. No anomalies detected.', '["Process payment", "Update claim status"]', true),
('de000003-0000-0000-0000-000000000003', 'c0000009-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000000', 'REJECT', 0.85, 'Multiple fraud indicators detected: Medical provider not in verified database, excessive billing patterns, soft tissue only claims matching known fraud pattern.', '["Refer to SIU", "Request additional documentation", "Contact policyholder"]', false);

-- Insert sample risk scores
INSERT INTO risk_scores (id, claim_id, run_id, overall_score, factors) VALUES
('05000001-0000-0000-0000-000000000001', 'c0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 0.10, '[{"name": "claim_amount", "score": 0.05, "weight": 0.3, "description": "Low claim amount within normal range"}, {"name": "claim_history", "score": 0.08, "weight": 0.3, "description": "No prior claims in 24 months"}, {"name": "documentation", "score": 0.12, "weight": 0.4, "description": "Complete documentation provided"}]'),
('05000002-0000-0000-0000-000000000002', 'c0000008-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000000', 0.85, '[{"name": "claim_amount", "score": 0.75, "weight": 0.3, "description": "High value total loss claim"}, {"name": "incident_circumstances", "score": 0.90, "weight": 0.4, "description": "Remote location, no witnesses"}, {"name": "documentation", "score": 0.88, "weight": 0.3, "description": "Document anomalies detected"}]');

-- Update fraud scenario hit counts based on inserted fraud hits
UPDATE fraud_scenarios SET hits_count = (
    SELECT COUNT(*) FROM fraud_hits WHERE fraud_hits.scenario_id = fraud_scenarios.id
);
