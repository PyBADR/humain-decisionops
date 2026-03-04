"""Decision Engine - Deterministic pipeline for claim evaluation.

Implements the full decision pipeline:
1. Receive claim
2. Extract features
3. Run fraud rules
4. Compute risk score
5. Apply policy rules
6. Build DecisionBundle
7. Persist decision + audit logs
8. Return DecisionBundle
"""

from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models.orm import (
    Claim as ClaimORM,
    Decision as DecisionORM,
    FraudHit as FraudHitORM,
    FraudScenario as FraudScenarioORM,
    RiskScore as RiskScoreORM,
    AuditEvent as AuditEventORM,
    Run as RunORM
)


class DecisionEngine:
    """Deterministic decision engine for insurance claims."""
    
    # Fraud rule weights
    FRAUD_WEIGHTS = {
        "large_claim_amount": 0.3,
        "duplicate_document": 0.4,
        "provider_out_of_network": 0.2,
        "recent_policy_change": 0.25,
        "multiple_claims_short_period": 0.35,
        "inconsistent_location": 0.15,
        "weekend_holiday_incident": 0.05,
        "high_risk_occupation": 0.1,
        "document_metadata_anomaly": 0.3,
        "velocity_check_failed": 0.2
    }
    
    # Policy average amounts by claim type
    POLICY_AVERAGES = {
        "medical reimbursement": 1500,
        "auto collision": 8000,
        "property damage": 25000,
        "auto theft": 20000,
        "dental": 500,
        "vision": 300,
        "default": 5000
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate(self, claim: ClaimORM, run: RunORM) -> Dict[str, Any]:
        """Run the full decision pipeline and return DecisionBundle."""
        
        # Step 1: Extract features
        features = self._extract_features(claim)
        self._log_audit(claim.id, run.id, "feature_extraction", {"features": features})
        
        # Step 2: Run fraud rules
        fraud_signals = self._run_fraud_rules(claim, features)
        self._log_audit(claim.id, run.id, "fraud_detection", {"signals": fraud_signals})
        
        # Step 3: Compute risk score
        risk_score = self._compute_risk_score(fraud_signals)
        self._persist_risk_score(claim, risk_score, fraud_signals)
        self._log_audit(claim.id, run.id, "risk_scoring", {"risk_score": risk_score})
        
        # Step 4: Apply policy rules
        policy_result = self._apply_policy_rules(claim, features)
        self._log_audit(claim.id, run.id, "policy_evaluation", policy_result)
        
        # Step 5: Make decision
        decision_status, confidence = self._make_decision(risk_score, policy_result)
        
        # Step 6: Generate rationale
        rationale = self._generate_rationale(claim, fraud_signals, risk_score, decision_status)
        
        # Step 7: Determine next actions
        next_actions = self._determine_next_actions(decision_status, fraud_signals)
        
        # Step 8: Build and persist DecisionBundle
        decision_bundle = self._build_decision_bundle(
            claim, run, decision_status, confidence, risk_score,
            fraud_signals, rationale, next_actions
        )
        
        # Persist decision
        self._persist_decision(claim, run, decision_bundle)
        
        # Update claim with decision
        claim.decision_status = decision_status
        claim.confidence = confidence
        claim.risk_score = risk_score
        claim.fraud_score = risk_score  # For compatibility
        claim.last_run_id = run.id
        self.db.commit()
        
        return decision_bundle
    
    def _extract_features(self, claim: ClaimORM) -> Dict[str, Any]:
        """Extract structured features from claim."""
        claim_type = (claim.claim_type or "default").lower()
        policy_avg = self.POLICY_AVERAGES.get(claim_type, self.POLICY_AVERAGES["default"])
        
        return {
            "claim_amount": float(claim.amount or 0),
            "claim_type": claim_type,
            "policy_average": policy_avg,
            "amount_ratio": float(claim.amount or 0) / policy_avg if policy_avg > 0 else 0,
            "incident_date": claim.incident_date.isoformat() if claim.incident_date else None,
            "incident_location": claim.incident_location,
            "customer_name": claim.customer_name,
            "policy_number": claim.policy_number,
            "fast_lane_eligible": claim.fast_lane_eligible
        }
    
    def _run_fraud_rules(self, claim: ClaimORM, features: Dict) -> List[Dict[str, Any]]:
        """Run fraud detection rules and return signals."""
        signals = []
        
        # Rule 1: Large claim amount (> 3x policy average)
        if features["amount_ratio"] > 3.0:
            signal = {
                "type": "large_claim_amount",
                "score": min(features["amount_ratio"] / 5.0, 1.0),
                "description": f"Claim amount ${features['claim_amount']:.2f} exceeds 3x policy average ${features['policy_average']:.2f}"
            }
            signals.append(signal)
            self._persist_fraud_hit(claim, "large_claim_amount", signal)
        
        # Rule 2: Weekend/Holiday incident (low weight)
        if claim.incident_date:
            if claim.incident_date.weekday() >= 5:  # Saturday or Sunday
                signal = {
                    "type": "weekend_holiday_incident",
                    "score": 0.3,
                    "description": "Incident occurred on weekend"
                }
                signals.append(signal)
        
        # Rule 3: High value claims (> $50,000)
        if features["claim_amount"] > 50000:
            signal = {
                "type": "high_value_claim",
                "score": 0.5,
                "description": f"High value claim: ${features['claim_amount']:.2f}"
            }
            signals.append(signal)
            self._persist_fraud_hit(claim, "high_value_claim", signal)
        
        # Rule 4: Velocity check - multiple claims (simulated)
        recent_claims = self.db.query(ClaimORM).filter(
            ClaimORM.customer_name == claim.customer_name,
            ClaimORM.id != claim.id
        ).count()
        
        if recent_claims >= 3:
            signal = {
                "type": "multiple_claims_short_period",
                "score": 0.6,
                "description": f"Customer has {recent_claims + 1} claims on record"
            }
            signals.append(signal)
            self._persist_fraud_hit(claim, "multiple_claims_short_period", signal)
        
        return signals
    
    def _compute_risk_score(self, fraud_signals: List[Dict]) -> float:
        """Compute overall risk score from fraud signals."""
        if not fraud_signals:
            return 0.1  # Base risk
        
        # Weighted sum of signal scores
        total_weight = 0
        weighted_score = 0
        
        for signal in fraud_signals:
            signal_type = signal["type"]
            weight = self.FRAUD_WEIGHTS.get(signal_type, 0.1)
            weighted_score += signal["score"] * weight
            total_weight += weight
        
        if total_weight > 0:
            risk_score = weighted_score / total_weight
        else:
            risk_score = 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, risk_score))
    
    def _apply_policy_rules(self, claim: ClaimORM, features: Dict) -> Dict[str, Any]:
        """Apply policy rules and return evaluation result."""
        exclusions = []
        coverage_valid = True
        
        # Check coverage limits
        claim_type = features["claim_type"]
        max_coverage = {
            "medical reimbursement": 100000,
            "auto collision": 50000,
            "property damage": 200000,
            "auto theft": 50000,
            "dental": 5000,
            "vision": 2000
        }.get(claim_type, 50000)
        
        if features["claim_amount"] > max_coverage:
            exclusions.append({
                "type": "coverage_limit_exceeded",
                "description": f"Claim ${features['claim_amount']:.2f} exceeds coverage limit ${max_coverage:.2f}"
            })
            coverage_valid = False
        
        return {
            "coverage_valid": coverage_valid,
            "exclusions": exclusions,
            "max_coverage": max_coverage,
            "policy_version": "v1.0"
        }
    
    def _make_decision(self, risk_score: float, policy_result: Dict) -> tuple:
        """Make final decision based on risk score and policy evaluation."""
        # If policy exclusions exist, require review
        if policy_result["exclusions"]:
            return "REVIEW", 0.7
        
        # Decision based on risk score
        if risk_score < 0.3:
            return "APPROVE", 1.0 - risk_score
        elif risk_score < 0.7:
            return "REVIEW", 0.5 + (0.7 - risk_score)
        else:
            return "REJECT", risk_score
    
    def _generate_rationale(self, claim: ClaimORM, fraud_signals: List, 
                           risk_score: float, decision: str) -> str:
        """Generate human-readable rationale for the decision."""
        parts = []
        
        if decision == "APPROVE":
            parts.append(f"Claim for ${claim.amount:.2f} approved.")
            parts.append(f"Risk score {risk_score:.2f} is within acceptable range.")
            if not fraud_signals:
                parts.append("No fraud signals detected.")
        
        elif decision == "REVIEW":
            parts.append(f"Claim for ${claim.amount:.2f} requires manual review.")
            parts.append(f"Risk score: {risk_score:.2f}")
            if fraud_signals:
                parts.append(f"Detected {len(fraud_signals)} potential fraud signal(s):")
                for sig in fraud_signals[:3]:  # Top 3
                    parts.append(f"  - {sig['description']}")
        
        else:  # REJECT
            parts.append(f"Claim for ${claim.amount:.2f} rejected.")
            parts.append(f"High risk score: {risk_score:.2f}")
            if fraud_signals:
                parts.append("Fraud indicators:")
                for sig in fraud_signals:
                    parts.append(f"  - {sig['description']}")
        
        return " ".join(parts)
    
    def _determine_next_actions(self, decision: str, fraud_signals: List) -> List[str]:
        """Determine next actions based on decision."""
        actions = []
        
        if decision == "APPROVE":
            actions.append("process_payment")
            actions.append("send_confirmation")
        
        elif decision == "REVIEW":
            actions.append("assign_to_adjuster")
            actions.append("request_additional_documentation")
            if any(s["type"] == "large_claim_amount" for s in fraud_signals):
                actions.append("verify_claim_amount")
        
        else:  # REJECT
            actions.append("send_rejection_notice")
            actions.append("log_fraud_investigation")
            if fraud_signals:
                actions.append("escalate_to_siu")  # Special Investigations Unit
        
        return actions
    
    def _build_decision_bundle(self, claim: ClaimORM, run: RunORM,
                               decision: str, confidence: float, risk_score: float,
                               fraud_signals: List, rationale: str, 
                               next_actions: List) -> Dict[str, Any]:
        """Build the DecisionBundle JSON structure."""
        return {
            "decision_id": str(uuid4()),
            "claim_id": str(claim.id),
            "decision": decision,
            "confidence": round(confidence, 4),
            "risk_score": round(risk_score, 4),
            "signals": [s["type"] for s in fraud_signals],
            "rationale": rationale,
            "next_actions": next_actions,
            "audit_log": {
                "policy_version": "v1.0",
                "pipeline_version": "v1",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "run_id": str(run.id),
                "provider": run.provider or "heuristic"
            }
        }
    
    def _persist_decision(self, claim: ClaimORM, run: RunORM, 
                         bundle: Dict[str, Any]) -> None:
        """Persist decision to database."""
        decision = DecisionORM(
            id=uuid4(),
            claim_id=claim.id,
            run_id=run.id,
            status=bundle["decision"],
            confidence=bundle["confidence"],
            rationale=bundle["rationale"],
            next_actions=bundle["next_actions"],
            auto_approved=bundle["decision"] == "APPROVE" and claim.fast_lane_eligible
        )
        self.db.add(decision)
        self.db.flush()
    
    def _persist_risk_score(self, claim: ClaimORM, risk_score: float, 
                           signals: List[Dict]) -> None:
        """Persist risk score to database."""
        factors = [s["type"] for s in signals]
        
        risk = RiskScoreORM(
            id=uuid4(),
            claim_id=claim.id,
            overall_score=risk_score,
            factors=factors
        )
        self.db.add(risk)
        self.db.flush()
    
    def _persist_fraud_hit(self, claim: ClaimORM, signal_type: str, 
                          signal: Dict) -> None:
        """Persist fraud hit to database."""
        # Find or create fraud scenario
        scenario = self.db.query(FraudScenarioORM).filter(
            FraudScenarioORM.name.ilike(f"%{signal_type.replace('_', ' ')}%")
        ).first()
        
        if not scenario:
            # Create scenario if not exists
            scenario = FraudScenarioORM(
                id=uuid4(),
                name=signal_type.replace("_", " ").title(),
                description=signal.get("description", ""),
                category="heuristic",
                threshold=0.5,
                enabled=True,
                hits_count=0
            )
            self.db.add(scenario)
            self.db.flush()
        
        # Create fraud hit
        hit = FraudHitORM(
            id=uuid4(),
            claim_id=claim.id,
            scenario_id=scenario.id,
            score=signal["score"],
            explanation=signal["description"]
        )
        self.db.add(hit)
        
        # Increment scenario hit count
        scenario.hits_count = (scenario.hits_count or 0) + 1
        self.db.flush()
    
    def _log_audit(self, claim_id, run_id, event_type: str, payload: Dict) -> None:
        """Log audit event."""
        audit = AuditEventORM(
            id=uuid4(),
            claim_id=claim_id,
            run_id=run_id,
            event_type=event_type,
            actor="decision_engine",
            payload=payload
        )
        self.db.add(audit)
        self.db.flush()
