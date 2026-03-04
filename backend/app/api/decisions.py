"""Decisions API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.database import get_db
from app.models.orm import Decision as DecisionORM, Claim as ClaimORM, Run as RunORM

router = APIRouter()


@router.get("/{decision_id}")
async def get_decision(decision_id: UUID, db: Session = Depends(get_db)):
    """Get a specific decision bundle by ID.
    
    Returns the full DecisionBundle structure as specified.
    """
    decision = db.query(DecisionORM).filter(DecisionORM.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    # Get associated claim for additional context
    claim = db.query(ClaimORM).filter(ClaimORM.id == decision.claim_id).first()
    
    # Get associated run for pipeline info
    run = db.query(RunORM).filter(RunORM.id == decision.run_id).first() if decision.run_id else None
    
    # Build DecisionBundle response
    return {
        "decision_id": str(decision.id),
        "claim_id": str(decision.claim_id),
        "decision": decision.status,  # APPROVE | REVIEW | REJECT
        "confidence": float(decision.confidence) if decision.confidence else 0.0,
        "risk_score": float(claim.risk_score) if claim and claim.risk_score else 0.0,
        "signals": decision.next_actions or [],  # Fraud signals detected
        "rationale": decision.rationale or "",
        "next_actions": decision.next_actions or [],
        "audit_log": {
            "policy_version": "v1.0",
            "pipeline_version": "v1",
            "timestamp": decision.created_at.isoformat() if decision.created_at else datetime.utcnow().isoformat(),
            "run_id": str(run.id) if run else None,
            "provider": run.provider if run else "heuristic",
            "duration_ms": run.duration_ms if run else None
        }
    }


@router.get("")
async def list_decisions(
    claim_id: Optional[UUID] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List all decisions with optional filters."""
    query = db.query(DecisionORM)
    
    if claim_id:
        query = query.filter(DecisionORM.claim_id == claim_id)
    
    if status:
        query = query.filter(DecisionORM.status == status)
    
    query = query.order_by(desc(DecisionORM.created_at))
    
    offset = (page - 1) * page_size
    decisions = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "decision_id": str(d.id),
            "claim_id": str(d.claim_id),
            "decision": d.status,
            "confidence": float(d.confidence) if d.confidence else 0.0,
            "rationale": d.rationale,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in decisions
    ]
