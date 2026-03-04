from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date
from pydantic import BaseModel

from app.models.database import get_db
from app.models.orm import (
    Claim as ClaimORM,
    ConversationTranscript as ConversationTranscriptORM,
    AuditEvent as AuditEventORM,
    Run as RunORM
)
from app.config import get_settings
from app.services.pipeline_runner import run_pipeline_async

router = APIRouter()
settings = get_settings()


class IntakeMessage(BaseModel):
    role: str
    content: str
    extracted_data: Optional[dict] = None


class IntakeRequest(BaseModel):
    messages: List[IntakeMessage]
    policy_number: str
    incident_date: str
    incident_location: str
    claim_type: str
    amount_estimate: float
    description: str


class IntakeResponse(BaseModel):
    claim_id: str
    claim_number: str
    run_id: str
    message: str


def generate_claim_number() -> str:
    import random
    year = datetime.now().year
    num = random.randint(1000, 9999)
    return f"CLM-{year}-{num}"


@router.post("/submit", response_model=IntakeResponse)
async def submit_intake(
    request: IntakeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit conversation intake and create claim."""
    
    # Create conversation transcript
    transcript = ConversationTranscriptORM(
        id=uuid4(),
        messages=[
            {
                "role": m.role,
                "content": m.content,
                "timestamp": datetime.utcnow().isoformat(),
                "extracted_data": m.extracted_data
            }
            for m in request.messages
        ],
        completed_at=datetime.utcnow()
    )
    db.add(transcript)
    db.flush()
    
    # Create claim from intake data
    claim = ClaimORM(
        id=uuid4(),
        claim_number=generate_claim_number(),
        customer_name="Intake Customer",  # Would be extracted from conversation
        policy_number=request.policy_number,
        claim_type=request.claim_type,
        amount=request.amount_estimate,
        currency="USD",
        incident_date=date.fromisoformat(request.incident_date),
        incident_location=request.incident_location,
        description=request.description,
        triage_label="REVIEW",
        decision_status="PENDING"
    )
    
    # Check fast lane eligibility
    if request.claim_type.lower() in ["medical reimbursement", "dental", "vision"] and request.amount_estimate < 1000:
        claim.fast_lane_eligible = True
    
    db.add(claim)
    db.flush()
    
    # Link transcript to claim
    transcript.claim_id = claim.id
    
    # Create run record
    run = RunORM(
        id=uuid4(),
        claim_id=claim.id,
        status="PENDING",
        provider="openai" if settings.use_openai else "ollama"
    )
    db.add(run)
    
    # Create audit events
    audit_intake = AuditEventORM(
        id=uuid4(),
        claim_id=claim.id,
        event_type="intake_completed",
        actor="system",
        payload={
            "source": "conversation_intake",
            "transcript_id": str(transcript.id),
            "message_count": len(request.messages)
        }
    )
    db.add(audit_intake)
    
    audit_claim = AuditEventORM(
        id=uuid4(),
        claim_id=claim.id,
        event_type="claim_created",
        actor="system",
        payload={"source": "intake"}
    )
    db.add(audit_claim)
    
    audit_pipeline = AuditEventORM(
        id=uuid4(),
        claim_id=claim.id,
        run_id=run.id,
        event_type="pipeline_started",
        actor="system",
        payload={"provider": run.provider}
    )
    db.add(audit_pipeline)
    
    db.commit()
    
    # Run pipeline in background
    background_tasks.add_task(run_pipeline_async, str(claim.id), str(run.id))
    
    return IntakeResponse(
        claim_id=str(claim.id),
        claim_number=claim.claim_number,
        run_id=str(run.id),
        message="Claim created and pipeline started"
    )


@router.get("/transcripts", response_model=List[dict])
async def list_transcripts(
    claim_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List conversation transcripts."""
    query = db.query(ConversationTranscriptORM)
    
    if claim_id:
        query = query.filter(ConversationTranscriptORM.claim_id == claim_id)
    
    query = query.order_by(ConversationTranscriptORM.created_at.desc())
    
    offset = (page - 1) * page_size
    transcripts = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "id": str(t.id),
            "claim_id": str(t.claim_id) if t.claim_id else None,
            "message_count": len(t.messages) if t.messages else 0,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None
        }
        for t in transcripts
    ]


@router.get("/transcripts/{transcript_id}", response_model=dict)
async def get_transcript(
    transcript_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific conversation transcript."""
    transcript = db.query(ConversationTranscriptORM).filter(
        ConversationTranscriptORM.id == transcript_id
    ).first()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return {
        "id": str(transcript.id),
        "claim_id": str(transcript.claim_id) if transcript.claim_id else None,
        "messages": transcript.messages,
        "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
        "completed_at": transcript.completed_at.isoformat() if transcript.completed_at else None
    }
