import pytest
from uuid import uuid4
import asyncio

from app.pipeline.graph import Pipeline, PipelineState, create_pipeline
from app.models.schemas import TriageLabel, DecisionStatus


class TestPipeline:
    @pytest.fixture
    def pipeline(self):
        return create_pipeline()
    
    @pytest.fixture
    def sample_state(self):
        return PipelineState(
            claim_id=uuid4(),
            run_id=uuid4(),
            claim_data={
                "claim_number": "CLM-2024-001",
                "customer_name": "Test Customer",
                "policy_number": "POL-123",
                "claim_type": "Medical Reimbursement",
                "amount": 500.00,
                "incident_date": "2024-01-15",
                "description": "Routine checkup reimbursement"
            }
        )
    
    def test_pipeline_creation(self, pipeline):
        assert pipeline is not None
        assert pipeline.provider in ["openai", "ollama", "mock"]
    
    @pytest.mark.asyncio
    async def test_ingest_document(self, pipeline, sample_state):
        # Mock db
        class MockDB:
            pass
        
        result = await pipeline._ingest_document(sample_state, MockDB())
        assert result.document_content is not None
    
    @pytest.mark.asyncio
    async def test_compute_risk_signals_low_amount(self, pipeline, sample_state):
        class MockDB:
            pass
        
        result = await pipeline._compute_risk_signals(sample_state, MockDB())
        
        assert len(result.risk_factors) == 3
        assert result.risk_score >= 0
        assert result.risk_score <= 1
    
    @pytest.mark.asyncio
    async def test_compute_risk_signals_high_amount(self, pipeline, sample_state):
        class MockDB:
            pass
        
        sample_state.claim_data["amount"] = 100000
        result = await pipeline._compute_risk_signals(sample_state, MockDB())
        
        # High amount should increase risk score
        assert result.risk_score > 0.3
    
    @pytest.mark.asyncio
    async def test_make_decision_stp(self, pipeline, sample_state):
        class MockDB:
            pass
        
        # Low risk, low fraud
        sample_state.risk_score = 0.1
        sample_state.fraud_score = 0.05
        
        result = await pipeline._make_decision(sample_state, MockDB())
        
        assert result.triage_label == TriageLabel.STP
        assert result.decision_status == DecisionStatus.APPROVE
        assert result.confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_make_decision_high_risk(self, pipeline, sample_state):
        class MockDB:
            pass
        
        # High fraud score
        sample_state.risk_score = 0.8
        sample_state.fraud_score = 0.75
        
        result = await pipeline._make_decision(sample_state, MockDB())
        
        assert result.triage_label == TriageLabel.HIGH_RISK
        assert result.decision_status == DecisionStatus.REVIEW
        assert result.confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_generate_rationale(self, pipeline, sample_state):
        class MockDB:
            pass
        
        sample_state.decision_status = DecisionStatus.APPROVE
        sample_state.risk_score = 0.1
        sample_state.fraud_score = 0.05
        sample_state.triage_label = TriageLabel.STP
        
        result = await pipeline._generate_rationale(sample_state, MockDB())
        
        assert result.rationale is not None
        assert len(result.rationale) > 0
    
    def test_default_rationale_approve(self, pipeline, sample_state):
        sample_state.decision_status = DecisionStatus.APPROVE
        sample_state.risk_score = 0.1
        sample_state.fraud_score = 0.05
        
        rationale = pipeline._default_rationale(sample_state)
        
        assert "approved" in rationale.lower()
    
    def test_default_rationale_review(self, pipeline, sample_state):
        sample_state.decision_status = DecisionStatus.REVIEW
        sample_state.risk_score = 0.5
        sample_state.fraud_score = 0.4
        
        rationale = pipeline._default_rationale(sample_state)
        
        assert "review" in rationale.lower()
    
    def test_default_extraction(self, pipeline, sample_state):
        extraction = pipeline._default_extraction(sample_state)
        
        assert extraction["service_type"] == "Medical Reimbursement"
        assert extraction["amount"] == 500.00
        assert extraction["patient_name"] == "Test Customer"


class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self):
        """Test complete pipeline execution with mock data."""
        pipeline = create_pipeline()
        
        state = PipelineState(
            claim_id=uuid4(),
            run_id=uuid4(),
            claim_data={
                "claim_number": "CLM-2024-TEST",
                "customer_name": "Integration Test",
                "policy_number": "POL-TEST",
                "claim_type": "Medical Reimbursement",
                "amount": 250.00,
                "incident_date": "2024-01-15",
                "description": "Test claim for integration"
            }
        )
        
        class MockDB:
            def query(self, model):
                return self
            def filter(self, *args, **kwargs):
                return self
            def all(self):
                return []
        
        # Run through key nodes
        state = await pipeline._ingest_document(state, MockDB())
        assert state.document_content is not None
        
        state = await pipeline._extract_structured_fields(state, MockDB())
        assert state.extracted_fields is not None
        
        state = await pipeline._compute_risk_signals(state, MockDB())
        assert len(state.risk_factors) > 0
        
        state = await pipeline._fraud_heuristics(state, MockDB())
        assert state.fraud_score >= 0
        
        state = await pipeline._make_decision(state, MockDB())
        assert state.decision_status is not None
        assert state.triage_label is not None
        
        state = await pipeline._generate_rationale(state, MockDB())
        assert state.rationale is not None
