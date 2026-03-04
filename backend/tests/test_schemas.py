import pytest
from uuid import uuid4
from datetime import datetime

from app.models.schemas import (
    Claim, ClaimCreate, ClaimUpdate,
    TriageLabel, DecisionStatus, ForensicsRisk, RunStatus,
    RiskFactor, ExtractedClaimFields, DecisionOutput,
    PipelineState
)


class TestClaimSchemas:
    def test_claim_create_valid(self):
        claim = ClaimCreate(
            customer_name="John Doe",
            policy_number="POL-123",
            claim_type="Medical",
            amount=500.00,
            incident_date="2024-01-15"
        )
        assert claim.customer_name == "John Doe"
        assert claim.amount == 500.00
    
    def test_claim_update_partial(self):
        update = ClaimUpdate(triage_label=TriageLabel.STP)
        assert update.triage_label == TriageLabel.STP
        assert update.fraud_score is None


class TestEnums:
    def test_triage_labels(self):
        assert TriageLabel.STP.value == "STP"
        assert TriageLabel.REVIEW.value == "REVIEW"
        assert TriageLabel.HIGH_RISK.value == "HIGH_RISK"
    
    def test_decision_status(self):
        assert DecisionStatus.APPROVE.value == "APPROVE"
        assert DecisionStatus.REJECT.value == "REJECT"
        assert DecisionStatus.REVIEW.value == "REVIEW"
        assert DecisionStatus.PENDING.value == "PENDING"
    
    def test_run_status(self):
        assert RunStatus.PENDING.value == "PENDING"
        assert RunStatus.RUNNING.value == "RUNNING"
        assert RunStatus.COMPLETED.value == "COMPLETED"
        assert RunStatus.FAILED.value == "FAILED"


class TestRiskFactor:
    def test_risk_factor_valid(self):
        factor = RiskFactor(
            name="claim_amount",
            score=0.5,
            weight=0.3,
            description="Moderate claim amount"
        )
        assert factor.name == "claim_amount"
        assert factor.score == 0.5
        assert factor.weight == 0.3


class TestExtractedClaimFields:
    def test_extracted_fields_defaults(self):
        fields = ExtractedClaimFields()
        assert fields.provider_name is None
        assert fields.diagnosis_codes == []
        assert fields.additional_info == {}
    
    def test_extracted_fields_with_data(self):
        fields = ExtractedClaimFields(
            provider_name="Test Provider",
            amount=1000.00,
            diagnosis_codes=["A01", "B02"]
        )
        assert fields.provider_name == "Test Provider"
        assert fields.amount == 1000.00
        assert len(fields.diagnosis_codes) == 2


class TestDecisionOutput:
    def test_decision_output_valid(self):
        decision = DecisionOutput(
            status=DecisionStatus.APPROVE,
            confidence=0.95,
            rationale="Claim approved based on analysis.",
            next_actions=["Process payment"]
        )
        assert decision.status == DecisionStatus.APPROVE
        assert decision.confidence == 0.95
    
    def test_decision_output_confidence_bounds(self):
        # Valid confidence
        decision = DecisionOutput(
            status=DecisionStatus.REVIEW,
            confidence=0.5,
            rationale="Review needed."
        )
        assert 0 <= decision.confidence <= 1


class TestPipelineState:
    def test_pipeline_state_init(self):
        state = PipelineState(
            claim_id=uuid4(),
            run_id=uuid4()
        )
        assert state.risk_score == 0
        assert state.fraud_score == 0
        assert state.policy_matches == []
        assert state.fraud_hits == []
    
    def test_pipeline_state_with_data(self):
        state = PipelineState(
            claim_id=uuid4(),
            run_id=uuid4(),
            claim_data={"amount": 1000},
            risk_score=0.5,
            fraud_score=0.3,
            triage_label=TriageLabel.REVIEW
        )
        assert state.claim_data["amount"] == 1000
        assert state.risk_score == 0.5
        assert state.triage_label == TriageLabel.REVIEW
