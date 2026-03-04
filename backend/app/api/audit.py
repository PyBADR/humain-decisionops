from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
import json
import csv
import io

from app.models.database import get_db
from app.models.orm import AuditEvent as AuditEventORM
from app.models.schemas import AuditEvent

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_audit_events(
    claim_id: Optional[UUID] = None,
    run_id: Optional[UUID] = None,
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """List audit events with filters."""
    query = db.query(AuditEventORM)
    
    if claim_id:
        query = query.filter(AuditEventORM.claim_id == claim_id)
    
    if run_id:
        query = query.filter(AuditEventORM.run_id == run_id)
    
    if event_type:
        query = query.filter(AuditEventORM.event_type == event_type)
    
    if actor:
        query = query.filter(AuditEventORM.actor == actor)
    
    query = query.order_by(desc(AuditEventORM.created_at))
    
    offset = (page - 1) * page_size
    events = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "id": str(e.id),
            "claim_id": str(e.claim_id) if e.claim_id else None,
            "run_id": str(e.run_id) if e.run_id else None,
            "event_type": e.event_type,
            "actor": e.actor,
            "payload": e.payload,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]


@router.get("/export/json")
async def export_audit_json(
    claim_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Export audit events as JSON."""
    query = db.query(AuditEventORM)
    
    if claim_id:
        query = query.filter(AuditEventORM.claim_id == claim_id)
    
    events = query.order_by(desc(AuditEventORM.created_at)).all()
    
    data = [
        {
            "id": str(e.id),
            "claim_id": str(e.claim_id) if e.claim_id else None,
            "run_id": str(e.run_id) if e.run_id else None,
            "event_type": e.event_type,
            "actor": e.actor,
            "payload": e.payload,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=audit_events.json"}
    )


@router.get("/export/csv")
async def export_audit_csv(
    claim_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Export audit events as CSV."""
    query = db.query(AuditEventORM)
    
    if claim_id:
        query = query.filter(AuditEventORM.claim_id == claim_id)
    
    events = query.order_by(desc(AuditEventORM.created_at)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "claim_id", "run_id", "event_type", "actor", "payload", "created_at"])
    
    for e in events:
        writer.writerow([
            str(e.id),
            str(e.claim_id) if e.claim_id else "",
            str(e.run_id) if e.run_id else "",
            e.event_type,
            e.actor,
            json.dumps(e.payload),
            e.created_at.isoformat()
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_events.csv"}
    )
