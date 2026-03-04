from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.models.database import get_db
from app.models.orm import (
    Claim as ClaimORM,
    FastLaneOverride as FastLaneOverrideORM,
    AuditEvent as AuditEventORM
)
from app.models.schemas import FastLaneOverrideCreate

router = APIRouter()


@router.get("/queue", response_model=List[dict])
async def get_fast_lane_queue(db: Session = Depends(get_db)):
    """Get claims eligible for fast lane processing."""
    claims = db.query(ClaimORM).filter(
        ClaimORM.fast_lane_eligible == True,
        ClaimORM.decision_status.in_(["PENDING", "APPROVE"])
    ).order_by(desc(ClaimORM.created_at)).all()
    
    return [
        {
            "id": str(c.id),
            "claim_number": c.claim_number,
            "customer_name": c.customer_name,
            "claim_type": c.claim_type,
            "amount": c.amount,
            "triage_label": c.triage_label,
            "fraud_score": c.fraud_score,
            "risk_score": c.risk_score,
            "decision_status": c.decision_status,
            "confidence": c.confidence,
            "auto_approve_ready": c.triage_label == "STP" and c.fraud_score < 0.2 and c.risk_score < 0.3,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in claims
    ]


@router.post("/{claim_id}/override", response_model=dict)
async def override_fast_lane(
    claim_id: UUID,
    reason: str,
    overridden_by: str = "reviewer",
    db: Session = Depends(get_db)
):
    """Override a fast lane claim to REVIEW status."""
    claim = db.query(ClaimORM).filter(ClaimORM.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if not claim.fast_lane_eligible:
        raise HTTPException(status_code=400, detail="Claim is not fast lane eligible")
    
    # Create override record
    override = FastLaneOverrideORM(
        id=uuid4(),
        claim_id=claim_id,
        reason=reason,
        overridden_by=overridden_by
    )
    db.add(override)
    
    # Update claim status
    claim.decision_status = "REVIEW"
    claim.fast_lane_eligible = False
    
    # Create audit event
    audit = AuditEventORM(
        id=uuid4(),
        claim_id=claim_id,
        event_type="fast_lane_override",
        actor=overridden_by,
        payload={
            "reason": reason,
            "previous_status": "APPROVE" if claim.decision_status == "APPROVE" else "PENDING"
        }
    )
    db.add(audit)
    
    db.commit()
    
    return {
        "claim_id": str(claim_id),
        "status": "REVIEW",
        "message": "Claim moved to review queue",
        "override_id": str(override.id)
    }


@router.get("/overrides", response_model=List[dict])
async def list_overrides(
    claim_id: UUID = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List fast lane overrides."""
    query = db.query(FastLaneOverrideORM)
    
    if claim_id:
        query = query.filter(FastLaneOverrideORM.claim_id == claim_id)
    
    query = query.order_by(desc(FastLaneOverrideORM.created_at))
    
    offset = (page - 1) * page_size
    overrides = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "id": str(o.id),
            "claim_id": str(o.claim_id),
            "reason": o.reason,
            "overridden_by": o.overridden_by,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in overrides
    ]
