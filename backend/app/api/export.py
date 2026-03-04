"""Export API endpoints for CSV and JSON downloads."""
import csv
import json
import io
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.database import get_db
from app.models.orm import Claim, AuditEvent

router = APIRouter(prefix="/api", tags=["export"])


def generate_csv(data: List[dict], fieldnames: List[str]) -> io.StringIO:
    """Generate CSV from list of dicts."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        # Convert non-string values to strings
        clean_row = {k: str(v) if v is not None else '' for k, v in row.items() if k in fieldnames}
        writer.writerow(clean_row)
    output.seek(0)
    return output


@router.get("/claims/export/csv")
async def export_claims_csv(
    triage_label: Optional[str] = None,
    decision_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export claims to CSV."""
    query = db.query(Claim)
    
    if triage_label:
        query = query.filter(Claim.triage_label == triage_label)
    if decision_status:
        query = query.filter(Claim.decision_status == decision_status)
    
    claims = query.order_by(Claim.created_at.desc()).all()
    
    fieldnames = [
        'claim_number', 'customer_name', 'customer_email', 'policy_number',
        'claim_type', 'amount', 'currency', 'incident_date', 'incident_location',
        'triage_label', 'fraud_score', 'risk_score', 'decision_status',
        'confidence', 'fast_lane_eligible', 'created_at', 'updated_at'
    ]
    
    data = []
    for claim in claims:
        data.append({
            'claim_number': claim.claim_number,
            'customer_name': claim.customer_name,
            'customer_email': claim.customer_email,
            'policy_number': claim.policy_number,
            'claim_type': claim.claim_type,
            'amount': claim.amount,
            'currency': claim.currency,
            'incident_date': claim.incident_date,
            'incident_location': claim.incident_location,
            'triage_label': claim.triage_label,
            'fraud_score': claim.fraud_score,
            'risk_score': claim.risk_score,
            'decision_status': claim.decision_status,
            'confidence': claim.confidence,
            'fast_lane_eligible': claim.fast_lane_eligible,
            'created_at': claim.created_at,
            'updated_at': claim.updated_at,
        })
    
    output = generate_csv(data, fieldnames)
    
    filename = f"claims_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/claims/export/json")
async def export_claims_json(
    triage_label: Optional[str] = None,
    decision_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export claims to JSON."""
    query = db.query(Claim)
    
    if triage_label:
        query = query.filter(Claim.triage_label == triage_label)
    if decision_status:
        query = query.filter(Claim.decision_status == decision_status)
    
    claims = query.order_by(Claim.created_at.desc()).all()
    
    data = []
    for claim in claims:
        data.append({
            'id': str(claim.id),
            'claim_number': claim.claim_number,
            'customer_name': claim.customer_name,
            'customer_email': claim.customer_email,
            'policy_number': claim.policy_number,
            'claim_type': claim.claim_type,
            'amount': float(claim.amount) if claim.amount else 0,
            'currency': claim.currency,
            'incident_date': str(claim.incident_date) if claim.incident_date else None,
            'incident_location': claim.incident_location,
            'triage_label': claim.triage_label,
            'fraud_score': float(claim.fraud_score) if claim.fraud_score else 0,
            'risk_score': float(claim.risk_score) if claim.risk_score else 0,
            'decision_status': claim.decision_status,
            'confidence': float(claim.confidence) if claim.confidence else 0,
            'fast_lane_eligible': claim.fast_lane_eligible,
            'created_at': claim.created_at.isoformat() if claim.created_at else None,
            'updated_at': claim.updated_at.isoformat() if claim.updated_at else None,
        })
    
    output = json.dumps(data, indent=2)
    filename = f"claims_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/audit/export/csv")
async def export_audit_csv(
    claim_id: Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export audit events to CSV."""
    query = db.query(AuditEvent)
    
    if claim_id:
        query = query.filter(AuditEvent.claim_id == claim_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    
    events = query.order_by(AuditEvent.created_at.desc()).all()
    
    fieldnames = ['id', 'claim_id', 'run_id', 'event_type', 'actor', 'payload', 'created_at']
    
    data = []
    for event in events:
        data.append({
            'id': str(event.id),
            'claim_id': str(event.claim_id) if event.claim_id else '',
            'run_id': str(event.run_id) if event.run_id else '',
            'event_type': event.event_type,
            'actor': event.actor,
            'payload': json.dumps(event.payload) if event.payload else '{}',
            'created_at': str(event.created_at),
        })
    
    output = generate_csv(data, fieldnames)
    
    filename = f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/audit/export/json")
async def export_audit_json(
    claim_id: Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export audit events to JSON."""
    query = db.query(AuditEvent)
    
    if claim_id:
        query = query.filter(AuditEvent.claim_id == claim_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    
    events = query.order_by(AuditEvent.created_at.desc()).all()
    
    data = []
    for event in events:
        data.append({
            'id': str(event.id),
            'claim_id': str(event.claim_id) if event.claim_id else None,
            'run_id': str(event.run_id) if event.run_id else None,
            'event_type': event.event_type,
            'actor': event.actor,
            'payload': event.payload,
            'created_at': event.created_at.isoformat() if event.created_at else None,
        })
    
    output = json.dumps(data, indent=2)
    filename = f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
