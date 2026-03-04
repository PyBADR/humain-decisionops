from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from uuid import UUID, uuid4
import os
import aiofiles
from datetime import datetime

from app.models.database import get_db
from app.models.orm import (
    Claim as ClaimORM,
    ClaimDocument as ClaimDocumentORM,
    DocForensicsSignal as DocForensicsSignalORM,
    Extraction as ExtractionORM,
    RiskScore as RiskScoreORM,
    Decision as DecisionORM,
    AuditEvent as AuditEventORM,
    Run as RunORM,
    FraudHit as FraudHitORM
)
from app.models.schemas import (
    Claim, ClaimCreate, ClaimList, ClaimUpdate,
    ClaimDocument, DocForensicsSignal,
    Extraction, RiskScore, Decision,
    RunPipelineResponse, RunStatus, AuditEventCreate
)
from app.config import get_settings
from app.services.pipeline_runner import run_pipeline_async

router = APIRouter()
settings = get_settings()


def generate_claim_number() -> str:
    """Generate a unique claim number."""
    import random
    year = datetime.now().year
    num = random.randint(1000, 9999)
    return f"CLM-{year}-{num}"


@router.post("", response_model=Claim)
async def create_claim(
    customer_name: str = Form(...),
    customer_email: Optional[str] = Form(None),
    policy_number: str = Form(...),
    claim_type: str = Form(...),
    amount: float = Form(...),
    currency: str = Form("USD"),
    incident_date: str = Form(...),
    incident_location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new claim with optional document upload."""
    from datetime import date
    
    # Create claim
    claim = ClaimORM(
        id=uuid4(),
        claim_number=generate_claim_number(),
        customer_name=customer_name,
        customer_email=customer_email,
        policy_number=policy_number,
        claim_type=claim_type,
        amount=amount,
        currency=currency,
        incident_date=date.fromisoformat(incident_date),
        incident_location=incident_location,
        description=description,
        triage_label="REVIEW",
        decision_status="PENDING"
    )
    
    # Determine fast lane eligibility
    if claim_type.lower() in ["medical reimbursement", "dental", "vision"] and amount < 1000:
        claim.fast_lane_eligible = True
    
    db.add(claim)
    db.flush()
    
    # Handle document upload
    if document:
        upload_dir = os.path.join(settings.upload_dir, str(claim.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, document.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await document.read()
            await f.write(content)
        
        doc = ClaimDocumentORM(
            id=uuid4(),
            claim_id=claim.id,
            filename=document.filename,
            file_type=document.content_type or "application/octet-stream",
            file_size=len(content),
            storage_path=file_path,
            forensics_risk="LOW"
        )
        db.add(doc)
    
    # Create audit event
    audit = AuditEventORM(
        id=uuid4(),
        claim_id=claim.id,
        event_type="claim_created",
        actor="system",
        payload={"source": "api"}
    )
    db.add(audit)
    
    db.commit()
    db.refresh(claim)
    
    return claim


@router.get("", response_model=List[ClaimList])
async def list_claims(
    search: Optional[str] = None,
    status: Optional[str] = None,
    triage: Optional[str] = None,
    fast_lane: Optional[bool] = None,
    fraud_hits: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List claims with filters."""
    query = db.query(ClaimORM)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (ClaimORM.claim_number.ilike(search_term)) |
            (ClaimORM.customer_name.ilike(search_term)) |
            (ClaimORM.policy_number.ilike(search_term))
        )
    
    if status:
        query = query.filter(ClaimORM.decision_status == status)
    
    if triage:
        query = query.filter(ClaimORM.triage_label == triage)
    
    if fast_lane is not None:
        query = query.filter(ClaimORM.fast_lane_eligible == fast_lane)
    
    if fraud_hits:
        # Filter claims that have fraud hits
        query = query.filter(ClaimORM.fraud_score > 0.5)
    
    query = query.order_by(desc(ClaimORM.updated_at))
    
    # Pagination
    offset = (page - 1) * page_size
    claims = query.offset(offset).limit(page_size).all()
    
    return claims


@router.get("/{claim_id}", response_model=dict)
async def get_claim(
    claim_id: UUID,
    db: Session = Depends(get_db)
):
    """Get claim details with all related data."""
    claim = db.query(ClaimORM).filter(ClaimORM.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Get related data
    documents = db.query(ClaimDocumentORM).filter(
        ClaimDocumentORM.claim_id == claim_id
    ).all()
    
    # Get forensics signals for documents
    doc_ids = [d.id for d in documents]
    forensics = db.query(DocForensicsSignalORM).filter(
        DocForensicsSignalORM.document_id.in_(doc_ids)
    ).all() if doc_ids else []
    
    extractions = db.query(ExtractionORM).filter(
        ExtractionORM.claim_id == claim_id
    ).order_by(desc(ExtractionORM.created_at)).first()
    
    risk_scores = db.query(RiskScoreORM).filter(
        RiskScoreORM.claim_id == claim_id
    ).order_by(desc(RiskScoreORM.created_at)).first()
    
    decision = db.query(DecisionORM).filter(
        DecisionORM.claim_id == claim_id
    ).order_by(desc(DecisionORM.created_at)).first()
    
    fraud_hits = db.query(FraudHitORM).filter(
        FraudHitORM.claim_id == claim_id
    ).all()
    
    runs = db.query(RunORM).filter(
        RunORM.claim_id == claim_id
    ).order_by(desc(RunORM.started_at)).all()
    
    return {
        "claim": {
            "id": str(claim.id),
            "claim_number": claim.claim_number,
            "customer_name": claim.customer_name,
            "customer_email": claim.customer_email,
            "policy_number": claim.policy_number,
            "claim_type": claim.claim_type,
            "amount": claim.amount,
            "currency": claim.currency,
            "incident_date": claim.incident_date.isoformat() if claim.incident_date else None,
            "incident_location": claim.incident_location,
            "description": claim.description,
            "triage_label": claim.triage_label,
            "fraud_score": claim.fraud_score,
            "risk_score": claim.risk_score,
            "decision_status": claim.decision_status,
            "confidence": claim.confidence,
            "fast_lane_eligible": claim.fast_lane_eligible,
            "last_run_id": str(claim.last_run_id) if claim.last_run_id else None,
            "created_at": claim.created_at.isoformat() if claim.created_at else None,
            "updated_at": claim.updated_at.isoformat() if claim.updated_at else None
        },
        "documents": [
            {
                "id": str(d.id),
                "filename": d.filename,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "forensics_risk": d.forensics_risk,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                "forensics_signals": [
                    {
                        "id": str(f.id),
                        "signal_type": f.signal_type,
                        "severity": f.severity,
                        "description": f.description,
                        "details": f.details
                    }
                    for f in forensics if f.document_id == d.id
                ]
            }
            for d in documents
        ],
        "extraction": {
            "id": str(extractions.id),
            "extracted_data": extractions.extracted_data,
            "schema_valid": extractions.schema_valid,
            "validation_errors": extractions.validation_errors,
            "created_at": extractions.created_at.isoformat()
        } if extractions else None,
        "risk_score": {
            "id": str(risk_scores.id),
            "overall_score": risk_scores.overall_score,
            "factors": risk_scores.factors,
            "created_at": risk_scores.created_at.isoformat()
        } if risk_scores else None,
        "decision": {
            "id": str(decision.id),
            "status": decision.status,
            "confidence": decision.confidence,
            "rationale": decision.rationale,
            "next_actions": decision.next_actions,
            "auto_approved": decision.auto_approved,
            "created_at": decision.created_at.isoformat()
        } if decision else None,
        "fraud_hits": [
            {
                "id": str(h.id),
                "scenario_id": str(h.scenario_id),
                "score": h.score,
                "explanation": h.explanation,
                "created_at": h.created_at.isoformat()
            }
            for h in fraud_hits
        ],
        "runs": [
            {
                "id": str(r.id),
                "status": r.status,
                "current_node": r.current_node,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "duration_ms": r.duration_ms,
                "provider": r.provider,
                "trace_id": r.trace_id
            }
            for r in runs
        ]
    }


@router.post("/{claim_id}/run", response_model=RunPipelineResponse)
async def run_claim_pipeline(
    claim_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run the decision pipeline for a claim."""
    claim = db.query(ClaimORM).filter(ClaimORM.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Create run record
    run = RunORM(
        id=uuid4(),
        claim_id=claim_id,
        status="PENDING",
        provider="openai" if settings.use_openai else "ollama"
    )
    db.add(run)
    
    # Create audit event
    audit = AuditEventORM(
        id=uuid4(),
        claim_id=claim_id,
        run_id=run.id,
        event_type="pipeline_started",
        actor="system",
        payload={"provider": run.provider}
    )
    db.add(audit)
    
    db.commit()
    
    # Run pipeline in background
    background_tasks.add_task(run_pipeline_async, str(claim_id), str(run.id))
    
    return RunPipelineResponse(
        run_id=run.id,
        status=RunStatus.PENDING,
        message="Pipeline started"
    )


@router.patch("/{claim_id}", response_model=Claim)
async def update_claim(
    claim_id: UUID,
    update: ClaimUpdate,
    db: Session = Depends(get_db)
):
    """Update claim fields."""
    claim = db.query(ClaimORM).filter(ClaimORM.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(claim, field, value)
    
    db.commit()
    db.refresh(claim)
    
    return claim
