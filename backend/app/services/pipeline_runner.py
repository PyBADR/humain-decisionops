import asyncio
from datetime import datetime
from uuid import UUID, uuid4
import structlog

from app.config import get_settings
from app.models.database import SessionLocal
from app.models.orm import (
    Claim as ClaimORM,
    Run as RunORM,
    Extraction as ExtractionORM,
    RiskScore as RiskScoreORM,
    Decision as DecisionORM,
    FraudHit as FraudHitORM,
    FraudScenario as FraudScenarioORM,
    AuditEvent as AuditEventORM,
    ClaimDocument as ClaimDocumentORM
)
from app.pipeline.graph import create_pipeline, PipelineState

settings = get_settings()
logger = structlog.get_logger()


async def run_pipeline_async(claim_id: str, run_id: str):
    """Run the decision pipeline asynchronously."""
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        # Get claim and run
        claim = db.query(ClaimORM).filter(ClaimORM.id == UUID(claim_id)).first()
        run = db.query(RunORM).filter(RunORM.id == UUID(run_id)).first()
        
        if not claim or not run:
            logger.error("claim_or_run_not_found", claim_id=claim_id, run_id=run_id)
            return
        
        # Update run status
        run.status = "RUNNING"
        run.current_node = "ingest_document"
        db.commit()
        
        # Create initial state
        initial_state = PipelineState(
            claim_id=UUID(claim_id),
            run_id=UUID(run_id),
            claim_data={
                "claim_number": claim.claim_number,
                "customer_name": claim.customer_name,
                "policy_number": claim.policy_number,
                "claim_type": claim.claim_type,
                "amount": claim.amount,
                "incident_date": claim.incident_date.isoformat() if claim.incident_date else None,
                "incident_location": claim.incident_location,
                "description": claim.description
            }
        )
        
        # Get document content if available
        doc = db.query(ClaimDocumentORM).filter(
            ClaimDocumentORM.claim_id == UUID(claim_id)
        ).first()
        
        if doc:
            initial_state.document_content = f"Document: {doc.filename}"
        
        # Create and run pipeline
        pipeline = create_pipeline()
        
        # Run pipeline nodes
        state = initial_state
        nodes = [
            "ingest_document",
            "extract_structured_fields",
            "retrieve_policy_context",
            "compute_risk_signals",
            "fraud_heuristics",
            "make_decision",
            "generate_rationale",
            "persist_all"
        ]
        
        for node_name in nodes:
            run.current_node = node_name
            db.commit()
            
            # Create audit event for node
            audit = AuditEventORM(
                id=uuid4(),
                claim_id=UUID(claim_id),
                run_id=UUID(run_id),
                event_type=f"node_{node_name}",
                actor="pipeline",
                payload={"status": "started"}
            )
            db.add(audit)
            db.commit()
            
            # Execute node
            try:
                state = await pipeline.execute_node(node_name, state, db)
            except Exception as e:
                logger.error("node_execution_error", node=node_name, error=str(e))
                state.error = str(e)
                break
        
        # Persist results
        await persist_pipeline_results(db, claim, run, state, start_time)
        
        # Update run status
        end_time = datetime.utcnow()
        run.status = "COMPLETED" if not state.error else "FAILED"
        run.completed_at = end_time
        run.duration_ms = int((end_time - start_time).total_seconds() * 1000)
        run.current_node = None
        
        if state.error:
            run.error_message = state.error
        
        # Update claim with results
        claim.last_run_id = UUID(run_id)
        claim.triage_label = state.triage_label.value if state.triage_label else "REVIEW"
        claim.fraud_score = state.fraud_score
        claim.risk_score = state.risk_score
        claim.decision_status = state.decision_status.value if state.decision_status else "REVIEW"
        claim.confidence = state.confidence
        
        db.commit()
        
        logger.info(
            "pipeline_completed",
            claim_id=claim_id,
            run_id=run_id,
            status=run.status,
            duration_ms=run.duration_ms
        )
        
    except Exception as e:
        logger.error("pipeline_error", claim_id=claim_id, run_id=run_id, error=str(e))
        
        # Update run as failed
        run = db.query(RunORM).filter(RunORM.id == UUID(run_id)).first()
        if run:
            run.status = "FAILED"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()
    
    finally:
        db.close()


async def persist_pipeline_results(db, claim, run, state: PipelineState, start_time: datetime):
    """Persist pipeline results to database."""
    run_id = run.id
    claim_id = claim.id
    
    # Persist extraction
    if state.extracted_fields:
        extraction = ExtractionORM(
            id=uuid4(),
            claim_id=claim_id,
            run_id=run_id,
            extracted_data=state.extracted_fields,
            schema_valid=True,
            validation_errors=[]
        )
        db.add(extraction)
    
    # Persist risk score
    if state.risk_factors:
        risk_score = RiskScoreORM(
            id=uuid4(),
            claim_id=claim_id,
            run_id=run_id,
            overall_score=state.risk_score,
            factors=[f.model_dump() if hasattr(f, 'model_dump') else f for f in state.risk_factors]
        )
        db.add(risk_score)
    
    # Persist fraud hits
    for hit in state.fraud_hits:
        scenario = db.query(FraudScenarioORM).filter(
            FraudScenarioORM.name == hit.get("scenario_name")
        ).first()
        
        if scenario:
            fraud_hit = FraudHitORM(
                id=uuid4(),
                claim_id=claim_id,
                run_id=run_id,
                scenario_id=scenario.id,
                score=hit.get("score", 0),
                explanation=hit.get("explanation", "")
            )
            db.add(fraud_hit)
            
            # Update scenario hit count
            scenario.hits_count += 1
    
    # Persist decision
    if state.decision_status:
        decision = DecisionORM(
            id=uuid4(),
            claim_id=claim_id,
            run_id=run_id,
            status=state.decision_status.value,
            confidence=state.confidence,
            rationale=state.rationale or "Decision made by automated pipeline.",
            next_actions=state.next_actions,
            auto_approved=state.triage_label and state.triage_label.value == "STP" and state.decision_status.value == "APPROVE"
        )
        db.add(decision)
    
    # Create final audit event
    audit = AuditEventORM(
        id=uuid4(),
        claim_id=claim_id,
        run_id=run_id,
        event_type="decision_made",
        actor="pipeline",
        payload={
            "status": state.decision_status.value if state.decision_status else "REVIEW",
            "confidence": state.confidence,
            "triage_label": state.triage_label.value if state.triage_label else "REVIEW",
            "fraud_score": state.fraud_score,
            "risk_score": state.risk_score
        }
    )
    db.add(audit)
    
    db.commit()
