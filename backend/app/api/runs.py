from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from app.models.database import get_db
from app.models.orm import Run as RunORM, AuditEvent as AuditEventORM
from app.models.schemas import Run

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_runs(
    claim_id: UUID = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List pipeline runs with filters."""
    query = db.query(RunORM)
    
    if claim_id:
        query = query.filter(RunORM.claim_id == claim_id)
    
    if status:
        query = query.filter(RunORM.status == status)
    
    query = query.order_by(desc(RunORM.started_at))
    
    offset = (page - 1) * page_size
    runs = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "id": str(r.id),
            "claim_id": str(r.claim_id),
            "status": r.status,
            "current_node": r.current_node,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "duration_ms": r.duration_ms,
            "provider": r.provider,
            "trace_id": r.trace_id,
            "error_message": r.error_message
        }
        for r in runs
    ]


@router.get("/{run_id}", response_model=dict)
async def get_run(
    run_id: UUID,
    db: Session = Depends(get_db)
):
    """Get run details with audit events."""
    run = db.query(RunORM).filter(RunORM.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Get audit events for this run
    events = db.query(AuditEventORM).filter(
        AuditEventORM.run_id == run_id
    ).order_by(AuditEventORM.created_at).all()
    
    return {
        "run": {
            "id": str(run.id),
            "claim_id": str(run.claim_id),
            "status": run.status,
            "current_node": run.current_node,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "duration_ms": run.duration_ms,
            "provider": run.provider,
            "trace_id": run.trace_id,
            "error_message": run.error_message
        },
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "actor": e.actor,
                "payload": e.payload,
                "created_at": e.created_at.isoformat()
            }
            for e in events
        ]
    }
