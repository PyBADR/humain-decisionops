from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID

from app.models.database import get_db
from app.models.orm import FraudScenario as FraudScenarioORM, FraudHit as FraudHitORM
from app.models.schemas import FraudScenario, FraudScenarioUpdate, FraudHit

router = APIRouter()


@router.get("/scenarios", response_model=List[dict])
async def list_fraud_scenarios(db: Session = Depends(get_db)):
    """List all fraud scenarios."""
    scenarios = db.query(FraudScenarioORM).order_by(
        desc(FraudScenarioORM.hits_count)
    ).all()
    
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "category": s.category,
            "description": s.description,
            "threshold": s.threshold,
            "enabled": s.enabled,
            "hits_count": s.hits_count,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in scenarios
    ]


@router.get("/scenarios/{scenario_id}", response_model=dict)
async def get_fraud_scenario(
    scenario_id: UUID,
    db: Session = Depends(get_db)
):
    """Get fraud scenario details with recent hits."""
    scenario = db.query(FraudScenarioORM).filter(
        FraudScenarioORM.id == scenario_id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get recent hits
    hits = db.query(FraudHitORM).filter(
        FraudHitORM.scenario_id == scenario_id
    ).order_by(desc(FraudHitORM.created_at)).limit(10).all()
    
    return {
        "scenario": {
            "id": str(scenario.id),
            "name": scenario.name,
            "category": scenario.category,
            "description": scenario.description,
            "threshold": scenario.threshold,
            "enabled": scenario.enabled,
            "hits_count": scenario.hits_count,
            "created_at": scenario.created_at.isoformat() if scenario.created_at else None
        },
        "recent_hits": [
            {
                "id": str(h.id),
                "claim_id": str(h.claim_id),
                "score": h.score,
                "explanation": h.explanation,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in hits
        ]
    }


@router.patch("/scenarios/{scenario_id}", response_model=dict)
async def update_fraud_scenario(
    scenario_id: UUID,
    update: FraudScenarioUpdate,
    db: Session = Depends(get_db)
):
    """Update fraud scenario threshold or enabled status."""
    scenario = db.query(FraudScenarioORM).filter(
        FraudScenarioORM.id == scenario_id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if update.threshold is not None:
        scenario.threshold = update.threshold
    
    if update.enabled is not None:
        scenario.enabled = update.enabled
    
    db.commit()
    db.refresh(scenario)
    
    return {
        "id": str(scenario.id),
        "name": scenario.name,
        "threshold": scenario.threshold,
        "enabled": scenario.enabled,
        "message": "Scenario updated successfully"
    }


@router.get("/hits", response_model=List[dict])
async def list_fraud_hits(
    claim_id: Optional[UUID] = None,
    scenario_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List fraud hits with filters."""
    query = db.query(FraudHitORM)
    
    if claim_id:
        query = query.filter(FraudHitORM.claim_id == claim_id)
    
    if scenario_id:
        query = query.filter(FraudHitORM.scenario_id == scenario_id)
    
    query = query.order_by(desc(FraudHitORM.created_at))
    
    offset = (page - 1) * page_size
    hits = query.offset(offset).limit(page_size).all()
    
    return [
        {
            "id": str(h.id),
            "claim_id": str(h.claim_id),
            "run_id": str(h.run_id),
            "scenario_id": str(h.scenario_id),
            "scenario_name": h.scenario.name if h.scenario else None,
            "score": h.score,
            "explanation": h.explanation,
            "created_at": h.created_at.isoformat() if h.created_at else None
        }
        for h in hits
    ]
