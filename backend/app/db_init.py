"""Database initialization module for HUMAIN DecisionOps.

Handles:
1. Import all ORM models (registers them with Base.metadata)
2. Guarded DB reset (drop_all + create_all) if RESET_DB_ON_STARTUP=true AND RESET_DB_CONFIRM=YES
3. Create all tables (if not reset)
4. Seed demo data if SEED_ON_STARTUP=true and tables are empty
"""
import os
import uuid
from datetime import date
import structlog
from sqlalchemy import text
from app.models.database import engine, Base, SessionLocal
# Import all ORM models to register with Base.metadata
from app.models import orm

logger = structlog.get_logger()


def init_database(seed_on_startup: bool = False) -> bool:
    """Initialize database: optionally reset, create tables, and seed."""
    logger.info("db.init.start", message="Starting database initialization")
    
    # Check for guarded reset flags
    reset_enabled = os.getenv("RESET_DB_ON_STARTUP", "false").lower() == "true"
    reset_confirmed = os.getenv("RESET_DB_CONFIRM", "NO").upper() == "YES"
    
    try:
        # Step 1: Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("db.init.connection.ok", message="Database connection successful")
        
        # Step 2: Guarded DB Reset (DEMO ONLY - requires both flags)
        if reset_enabled and reset_confirmed:
            logger.warning("db.reset.enabled", message="⚠️ DB RESET ENABLED: dropping all tables")
            Base.metadata.drop_all(bind=engine)
            logger.info("db.reset.drop_all.done", message="All tables dropped")
            Base.metadata.create_all(bind=engine)
            logger.info("db.reset.create_all.done", message="All tables recreated with ORM schema")
            # Force seed after reset
            seed_database(force=True)
        else:
            # Normal flow: create tables if not exist
            Base.metadata.create_all(bind=engine)
            logger.info("db.init.create_all.done", message="Database tables ensured")
            # Seed if enabled and empty
            if seed_on_startup:
                seed_database(force=False)
        
        logger.info("db.init.complete", message="Database initialization complete")
        return True
        
    except Exception as e:
        logger.error("db.init.failed", error=str(e), exc_info=True)
        return False


def seed_database(force: bool = False) -> bool:
    """Seed database with demo data. If force=True, always seed. Otherwise only if empty."""
    db = SessionLocal()
    try:
        if not force:
            existing = db.query(orm.Claim).first()
            if existing:
                logger.info("db.seed.skipped", message="Database already contains data")
                return True
        
        logger.info("db.seed.start", message="Seeding demo data", force=force)
        
        # Clear existing data if force seeding
        if force:
            db.query(orm.FraudHit).delete()
            db.query(orm.FraudScenario).delete()
            db.query(orm.PolicyDocument).delete()
            db.query(orm.Claim).delete()
            db.commit()
        
        # Demo claims (12 claims)
        claims = create_demo_claims()
        # Fraud scenarios (12 scenarios)
        scenarios = create_demo_fraud_scenarios()
        # Policy documents (2 documents)
        policy_docs = create_demo_policy_docs()
        
        db.add_all(claims)
        db.add_all(scenarios)
        db.add_all(policy_docs)
        db.commit()
        
        logger.info("db.seed.done", claims=len(claims), scenarios=len(scenarios), policy_docs=len(policy_docs))
        return True
        
    except Exception as e:
        logger.error("db.seed.failed", error=str(e), exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()


def create_demo_claims():
    """Create 12 demo claims."""
    return [
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-001", customer_name="John Smith", customer_email="john@example.com", policy_number="POL-2024-001", claim_type="Medical Reimbursement", amount=1250.00, incident_date=date(2024, 1, 15), incident_location="Seattle, WA", description="Routine checkup and lab work", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.15, confidence=0.95),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-002", customer_name="Sarah Johnson", customer_email="sarah@example.com", policy_number="POL-2024-002", claim_type="Auto Collision", amount=8500.00, incident_date=date(2024, 1, 18), incident_location="Portland, OR", description="Rear-end collision at intersection", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.3, risk_score=0.4),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-003", customer_name="Michael Chen", customer_email="michael@example.com", policy_number="POL-2024-003", claim_type="Property Damage", amount=45000.00, incident_date=date(2024, 1, 20), incident_location="San Francisco, CA", description="Water damage from burst pipe", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.82, risk_score=0.75),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-004", customer_name="Emily Davis", customer_email="emily@example.com", policy_number="POL-2024-004", claim_type="Medical Reimbursement", amount=350.00, incident_date=date(2024, 1, 22), incident_location="Los Angeles, CA", description="Prescription medication refill", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.05, risk_score=0.08, confidence=0.98),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-005", customer_name="Robert Wilson", customer_email="robert@example.com", policy_number="POL-2024-005", claim_type="Auto Theft", amount=32000.00, incident_date=date(2024, 1, 25), incident_location="Denver, CO", description="Vehicle stolen from parking garage", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.75, risk_score=0.78),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-006", customer_name="Lisa Anderson", customer_email="lisa@example.com", policy_number="POL-2024-006", claim_type="Medical Reimbursement", amount=2100.00, incident_date=date(2024, 1, 28), incident_location="Austin, TX", description="Emergency room visit", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.2, risk_score=0.25),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-007", customer_name="David Martinez", customer_email="david@example.com", policy_number="POL-2024-007", claim_type="Property Damage", amount=12500.00, incident_date=date(2024, 2, 1), incident_location="Phoenix, AZ", description="Fire damage to kitchen", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.35, risk_score=0.4),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-008", customer_name="Jennifer Taylor", customer_email="jennifer@example.com", policy_number="POL-2024-008", claim_type="Medical Reimbursement", amount=890.00, incident_date=date(2024, 2, 3), incident_location="Chicago, IL", description="Physical therapy sessions", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.18, confidence=0.92),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-009", customer_name="James Brown", customer_email="james@example.com", policy_number="POL-2024-009", claim_type="Auto Collision", amount=15000.00, incident_date=date(2024, 2, 5), incident_location="Miami, FL", description="Multi-vehicle accident on highway", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.68, risk_score=0.7),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-010", customer_name="Amanda White", customer_email="amanda@example.com", policy_number="POL-2024-010", claim_type="Medical Reimbursement", amount=450.00, incident_date=date(2024, 2, 8), incident_location="Boston, MA", description="Annual dental cleaning", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.02, risk_score=0.05, confidence=0.97),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-011", customer_name="Christopher Lee", customer_email="chris@example.com", policy_number="POL-2024-011", claim_type="Property Damage", amount=78000.00, incident_date=date(2024, 2, 10), incident_location="New York, NY", description="Storm damage to roof and siding", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.88, risk_score=0.85),
        orm.Claim(id=uuid.uuid4(), claim_number="CLM-012", customer_name="Michelle Garcia", customer_email="michelle@example.com", policy_number="POL-2024-012", claim_type="Auto Collision", amount=4200.00, incident_date=date(2024, 2, 12), incident_location="Seattle, WA", description="Minor fender bender in parking lot", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.15, risk_score=0.2),
    ]


def create_demo_fraud_scenarios():
    """Create 12 demo fraud scenarios."""
    return [
        orm.FraudScenario(id=uuid.uuid4(), name="Excessive Claim Amount", description="Claim amount exceeds 3x policy average", category="Amount", threshold=0.7, enabled=True, hits_count=5),
        orm.FraudScenario(id=uuid.uuid4(), name="Duplicate Document Hash", description="Same document submitted for multiple claims", category="Document", threshold=0.9, enabled=True, hits_count=2),
        orm.FraudScenario(id=uuid.uuid4(), name="Out-of-Network Provider", description="Service provider not in approved network", category="Provider", threshold=0.5, enabled=True, hits_count=8),
        orm.FraudScenario(id=uuid.uuid4(), name="Recent Policy Change", description="Coverage increased within 30 days of claim", category="Policy", threshold=0.6, enabled=True, hits_count=3),
        orm.FraudScenario(id=uuid.uuid4(), name="Multiple Claims Short Period", description="More than 3 claims in 90 days", category="Frequency", threshold=0.8, enabled=True, hits_count=4),
        orm.FraudScenario(id=uuid.uuid4(), name="Inconsistent Location Data", description="Incident location differs from policy address", category="Location", threshold=0.5, enabled=True, hits_count=6),
        orm.FraudScenario(id=uuid.uuid4(), name="Weekend/Holiday Incident", description="Incident occurred on weekend or holiday", category="Timing", threshold=0.3, enabled=True, hits_count=12),
        orm.FraudScenario(id=uuid.uuid4(), name="High-Risk Occupation", description="Claimant in high-risk occupation category", category="Profile", threshold=0.4, enabled=True, hits_count=7),
        orm.FraudScenario(id=uuid.uuid4(), name="Document Metadata Anomaly", description="PDF creation date after incident date", category="Document", threshold=0.85, enabled=True, hits_count=1),
        orm.FraudScenario(id=uuid.uuid4(), name="Velocity Check Failed", description="Claim submitted too quickly after incident", category="Timing", threshold=0.6, enabled=True, hits_count=3),
        orm.FraudScenario(id=uuid.uuid4(), name="Known Fraud Ring Association", description="Address or phone linked to known fraud", category="Network", threshold=0.95, enabled=True, hits_count=0),
        orm.FraudScenario(id=uuid.uuid4(), name="Template Invoice Detected", description="Invoice matches known fraudulent template", category="Document", threshold=0.9, enabled=True, hits_count=2),
    ]


def create_demo_policy_docs():
    """Create 2 demo policy documents."""
    return [
        orm.PolicyDocument(id=uuid.uuid4(), name="Standard Medical Policy", filename="medical_policy.pdf", file_type="pdf", storage_path="/policies/medical_policy.pdf", indexed=True, chunk_count=5),
        orm.PolicyDocument(id=uuid.uuid4(), name="Auto Insurance Policy", filename="auto_policy.pdf", file_type="pdf", storage_path="/policies/auto_policy.pdf", indexed=True, chunk_count=3),
    ]


def seed_if_empty() -> bool:
    """Seed database with demo data if claims table is empty. Idempotent."""
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(orm.Claim).first()
        if existing:
            logger.info("db.init.seed.skipped", message="Database already contains data")
            return True
        
        logger.info("db.init.seed.start", message="Seeding demo data")
        
        # Demo claims (12 claims)
        claims = [
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-001", customer_name="John Smith", customer_email="john@example.com", policy_number="POL-2024-001", claim_type="Medical Reimbursement", amount=1250.00, incident_date=date(2024, 1, 15), incident_location="Seattle, WA", description="Routine checkup and lab work", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.15, confidence=0.95),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-002", customer_name="Sarah Johnson", customer_email="sarah@example.com", policy_number="POL-2024-002", claim_type="Auto Collision", amount=8500.00, incident_date=date(2024, 1, 18), incident_location="Portland, OR", description="Rear-end collision at intersection", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.3, risk_score=0.4),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-003", customer_name="Michael Chen", customer_email="michael@example.com", policy_number="POL-2024-003", claim_type="Property Damage", amount=45000.00, incident_date=date(2024, 1, 20), incident_location="San Francisco, CA", description="Water damage from burst pipe", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.82, risk_score=0.75),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-004", customer_name="Emily Davis", customer_email="emily@example.com", policy_number="POL-2024-004", claim_type="Medical Reimbursement", amount=350.00, incident_date=date(2024, 1, 22), incident_location="Los Angeles, CA", description="Prescription medication refill", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.05, risk_score=0.08, confidence=0.98),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-005", customer_name="Robert Wilson", customer_email="robert@example.com", policy_number="POL-2024-005", claim_type="Auto Theft", amount=32000.00, incident_date=date(2024, 1, 25), incident_location="Denver, CO", description="Vehicle stolen from parking garage", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.75, risk_score=0.78),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-006", customer_name="Lisa Anderson", customer_email="lisa@example.com", policy_number="POL-2024-006", claim_type="Medical Reimbursement", amount=2100.00, incident_date=date(2024, 1, 28), incident_location="Austin, TX", description="Emergency room visit", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.2, risk_score=0.25),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-007", customer_name="David Martinez", customer_email="david@example.com", policy_number="POL-2024-007", claim_type="Property Damage", amount=12500.00, incident_date=date(2024, 2, 1), incident_location="Phoenix, AZ", description="Fire damage to kitchen", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.35, risk_score=0.4),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-008", customer_name="Jennifer Taylor", customer_email="jennifer@example.com", policy_number="POL-2024-008", claim_type="Medical Reimbursement", amount=890.00, incident_date=date(2024, 2, 3), incident_location="Chicago, IL", description="Physical therapy sessions", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.1, risk_score=0.18, confidence=0.92),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-009", customer_name="James Brown", customer_email="james@example.com", policy_number="POL-2024-009", claim_type="Auto Collision", amount=15000.00, incident_date=date(2024, 2, 5), incident_location="Miami, FL", description="Multi-vehicle accident on highway", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.68, risk_score=0.7),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-010", customer_name="Amanda White", customer_email="amanda@example.com", policy_number="POL-2024-010", claim_type="Medical Reimbursement", amount=450.00, incident_date=date(2024, 2, 8), incident_location="Boston, MA", description="Annual dental cleaning", decision_status="APPROVED", triage_label="STP", fast_lane_eligible=True, fraud_score=0.02, risk_score=0.05, confidence=0.97),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-011", customer_name="Christopher Lee", customer_email="chris@example.com", policy_number="POL-2024-011", claim_type="Property Damage", amount=78000.00, incident_date=date(2024, 2, 10), incident_location="New York, NY", description="Storm damage to roof and siding", decision_status="PENDING", triage_label="HIGH_RISK", fast_lane_eligible=False, fraud_score=0.88, risk_score=0.85),
            orm.Claim(id=uuid.uuid4(), claim_number="CLM-012", customer_name="Michelle Garcia", customer_email="michelle@example.com", policy_number="POL-2024-012", claim_type="Auto Collision", amount=4200.00, incident_date=date(2024, 2, 12), incident_location="Seattle, WA", description="Minor fender bender in parking lot", decision_status="PENDING", triage_label="REVIEW", fast_lane_eligible=False, fraud_score=0.15, risk_score=0.2),
        ]
        
        # Fraud scenarios (12 scenarios)
        scenarios = [
            orm.FraudScenario(id=uuid.uuid4(), name="Excessive Claim Amount", description="Claim amount exceeds 3x policy average", category="Amount", threshold=0.7, enabled=True, hits_count=5),
            orm.FraudScenario(id=uuid.uuid4(), name="Duplicate Document Hash", description="Same document submitted for multiple claims", category="Document", threshold=0.9, enabled=True, hits_count=2),
            orm.FraudScenario(id=uuid.uuid4(), name="Out-of-Network Provider", description="Service provider not in approved network", category="Provider", threshold=0.5, enabled=True, hits_count=8),
            orm.FraudScenario(id=uuid.uuid4(), name="Recent Policy Change", description="Coverage increased within 30 days of claim", category="Policy", threshold=0.6, enabled=True, hits_count=3),
            orm.FraudScenario(id=uuid.uuid4(), name="Multiple Claims Short Period", description="More than 3 claims in 90 days", category="Frequency", threshold=0.8, enabled=True, hits_count=4),
            orm.FraudScenario(id=uuid.uuid4(), name="Inconsistent Location Data", description="Incident location differs from policy address", category="Location", threshold=0.5, enabled=True, hits_count=6),
            orm.FraudScenario(id=uuid.uuid4(), name="Weekend/Holiday Incident", description="Incident occurred on weekend or holiday", category="Timing", threshold=0.3, enabled=True, hits_count=12),
            orm.FraudScenario(id=uuid.uuid4(), name="High-Risk Occupation", description="Claimant in high-risk occupation category", category="Profile", threshold=0.4, enabled=True, hits_count=7),
            orm.FraudScenario(id=uuid.uuid4(), name="Document Metadata Anomaly", description="PDF creation date after incident date", category="Document", threshold=0.85, enabled=True, hits_count=1),
            orm.FraudScenario(id=uuid.uuid4(), name="Velocity Check Failed", description="Claim submitted too quickly after incident", category="Timing", threshold=0.6, enabled=True, hits_count=3),
            orm.FraudScenario(id=uuid.uuid4(), name="Known Fraud Ring Association", description="Address or phone linked to known fraud", category="Network", threshold=0.95, enabled=True, hits_count=0),
            orm.FraudScenario(id=uuid.uuid4(), name="Template Invoice Detected", description="Invoice matches known fraudulent template", category="Document", threshold=0.9, enabled=True, hits_count=2),
        ]
        
        # Policy documents (2 documents)
        policy_docs = [
            orm.PolicyDocument(id=uuid.uuid4(), name="Standard Medical Policy", filename="medical_policy.pdf", file_type="pdf", storage_path="/policies/medical_policy.pdf", indexed=True, chunk_count=5),
            orm.PolicyDocument(id=uuid.uuid4(), name="Auto Insurance Policy", filename="auto_policy.pdf", file_type="pdf", storage_path="/policies/auto_policy.pdf", indexed=True, chunk_count=3),
        ]
        
        db.add_all(claims)
        db.add_all(scenarios)
        db.add_all(policy_docs)
        db.commit()
        
        logger.info("db.init.seed.done", claims=len(claims), scenarios=len(scenarios), policy_docs=len(policy_docs))
        return True
        
    except Exception as e:
        logger.error("db.init.seed.failed", error=str(e), exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()
