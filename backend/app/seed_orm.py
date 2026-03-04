"""ORM-based database seeding for HUMAIN DecisionOps."""
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.orm import Claim, FraudScenario
import structlog

logger = structlog.get_logger()

def run_seed():
    """Seed database with demo data using ORM models."""
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Claim).first()
        if existing:
            logger.info("seed_skipped", message="Database already contains data")
            return True
        
        # Demo claims
        claims = [
            Claim(id=uuid.uuid4(), claim_number="CLM-001", customer_name="John Smith", customer_email="john@example.com", policy_number="POL-2024-001", claim_type="Medical Reimbursement", amount=1250.00, incident_date=date(2024, 1, 15), incident_location="Seattle, WA", description="Routine checkup and lab work", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.15, confidence=0.95),
            Claim(id=uuid.uuid4(), claim_number="CLM-002", customer_name="Sarah Johnson", customer_email="sarah@example.com", policy_number="POL-2024-002", claim_type="Auto Collision", amount=8500.00, incident_date=date(2024, 1, 18), incident_location="Portland, OR", description="Rear-end collision at intersection", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.3, risk_score=0.4),
            Claim(id=uuid.uuid4(), claim_number="CLM-003", customer_name="Michael Chen", customer_email="michael@example.com", policy_number="POL-2024-003", claim_type="Property Damage", amount=45000.00, incident_date=date(2024, 1, 20), incident_location="San Francisco, CA", description="Water damage from burst pipe", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.82, risk_score=0.75),
            Claim(id=uuid.uuid4(), claim_number="CLM-004", customer_name="Emily Davis", customer_email="emily@example.com", policy_number="POL-2024-004", claim_type="Medical Reimbursement", amount=350.00, incident_date=date(2024, 1, 22), incident_location="Los Angeles, CA", description="Prescription medication refill", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.05, risk_score=0.08, confidence=0.98),
            Claim(id=uuid.uuid4(), claim_number="CLM-005", customer_name="Robert Wilson", customer_email="robert@example.com", policy_number="POL-2024-005", claim_type="Auto Theft", amount=32000.00, incident_date=date(2024, 1, 25), incident_location="Denver, CO", description="Vehicle stolen from parking garage", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.75, risk_score=0.78),
            Claim(id=uuid.uuid4(), claim_number="CLM-006", customer_name="Lisa Anderson", customer_email="lisa@example.com", policy_number="POL-2024-006", claim_type="Medical Reimbursement", amount=2100.00, incident_date=date(2024, 1, 28), incident_location="Austin, TX", description="Emergency room visit", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.2, risk_score=0.25),
            Claim(id=uuid.uuid4(), claim_number="CLM-007", customer_name="David Martinez", customer_email="david@example.com", policy_number="POL-2024-007", claim_type="Property Damage", amount=12500.00, incident_date=date(2024, 2, 1), incident_location="Phoenix, AZ", description="Fire damage to kitchen", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.35, risk_score=0.4),
            Claim(id=uuid.uuid4(), claim_number="CLM-008", customer_name="Jennifer Taylor", customer_email="jennifer@example.com", policy_number="POL-2024-008", claim_type="Medical Reimbursement", amount=890.00, incident_date=date(2024, 2, 3), incident_location="Chicago, IL", description="Physical therapy sessions", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.18, confidence=0.92),
            Claim(id=uuid.uuid4(), claim_number="CLM-009", customer_name="James Brown", customer_email="james@example.com", policy_number="POL-2024-009", claim_type="Auto Collision", amount=15000.00, incident_date=date(2024, 2, 5), incident_location="Miami, FL", description="Multi-vehicle accident on highway", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.68, risk_score=0.7),
            Claim(id=uuid.uuid4(), claim_number="CLM-010", customer_name="Amanda White", customer_email="amanda@example.com", policy_number="POL-2024-010", claim_type="Medical Reimbursement", amount=450.00, incident_date=date(2024, 2, 8), incident_location="Boston, MA", description="Annual dental cleaning", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.02, risk_score=0.05, confidence=0.97),
            Claim(id=uuid.uuid4(), claim_number="CLM-011", customer_name="Christopher Lee", customer_email="chris@example.com", policy_number="POL-2024-011", claim_type="Property Damage", amount=78000.00, incident_date=date(2024, 2, 10), incident_location="New York, NY", description="Storm damage to roof and siding", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.88, risk_score=0.85),
            Claim(id=uuid.uuid4(), claim_number="CLM-012", customer_name="Michelle Garcia", customer_email="michelle@example.com", policy_number="POL-2024-012", claim_type="Auto Collision", amount=4200.00, incident_date=date(2024, 2, 12), incident_location="Seattle, WA", description="Minor fender bender in parking lot", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.15, risk_score=0.2),
        ]
        
        # Fraud scenarios
        scenarios = [
            FraudScenario(id=uuid.uuid4(), name="Excessive Claim Amount", description="Claim amount exceeds 3x policy average", category="Amount", threshold=0.7, enabled=True, hits_count=5),
            FraudScenario(id=uuid.uuid4(), name="Duplicate Document Hash", description="Same document submitted for multiple claims", category="Document", threshold=0.9, enabled=True, hits_count=2),
            FraudScenario(id=uuid.uuid4(), name="Out-of-Network Provider", description="Service provider not in approved network", category="Provider", threshold=0.5, enabled=True, hits_count=8),
            FraudScenario(id=uuid.uuid4(), name="Recent Policy Change", description="Coverage increased within 30 days of claim", category="Policy", threshold=0.6, enabled=True, hits_count=3),
            FraudScenario(id=uuid.uuid4(), name="Multiple Claims Short Period", description="More than 3 claims in 90 days", category="Frequency", threshold=0.8, enabled=True, hits_count=4),
            FraudScenario(id=uuid.uuid4(), name="Inconsistent Location Data", description="Incident location differs from policy address", category="Location", threshold=0.5, enabled=True, hits_count=6),
        ]
        
        db.add_all(claims)
        db.add_all(scenarios)
        db.commit()
        
        logger.info("seed_completed", claims=len(claims), scenarios=len(scenarios))
        return True
    except Exception as e:
        logger.error("seed_failed", error=str(e))
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
