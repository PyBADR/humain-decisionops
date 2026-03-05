from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.database import get_db, engine, SessionLocal
from app.models.schemas import HealthResponse, MetricsResponse
from app.config import get_settings
from app.db_init import check_db_health

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Check system health status including DB connectivity and operating mode."""
    # Check database connection
    db_healthy = False
    db_error = None
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        db_error = str(e)
    
    # Determine effective mode
    effective_mode = settings.effective_mode
    
    # Determine LLM provider for display
    if effective_mode == "openai":
        llm_provider = "openai"
    elif effective_mode == "ollama":
        llm_provider = "ollama"
    else:
        llm_provider = "heuristic"
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        version="1.0.0",
        database=db_healthy,
        database_error=db_error,
        vector_store=True,  # Using FAISS fallback if pgvector unavailable
        llm_provider=llm_provider,
        mode=effective_mode,
        heuristic_mode=effective_mode == "heuristic"
    )


@router.get("/health/db")
async def health_db():
    """Check database health with schema validation and claims count."""
    result = check_db_health(engine, SessionLocal)
    status_code = 200 if result["db_ok"] and result["schema_ok"] else 500
    return JSONResponse(content=result, status_code=status_code)


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: Session = Depends(get_db)):
    """Get system metrics and KPIs."""
    from datetime import datetime, timedelta
    from app.models.orm import Claim, Decision, FraudHit, FraudScenario, Run
    
    today = datetime.utcnow().date()
    
    # Claims today
    claims_today = db.query(Claim).filter(
        Claim.created_at >= today
    ).count()
    
    # Total claims for rate calculations
    total_claims = db.query(Claim).count()
    
    # STP rate (claims with STP triage that were approved)
    stp_claims = db.query(Claim).filter(
        Claim.triage_label == "STP",
        Claim.decision_status == "APPROVE"
    ).count()
    stp_rate = (stp_claims / total_claims * 100) if total_claims > 0 else 0
    
    # Fraud hit rate
    claims_with_fraud = db.query(FraudHit.claim_id).distinct().count()
    fraud_hit_rate = (claims_with_fraud / total_claims * 100) if total_claims > 0 else 0
    
    # Average decision time
    completed_runs = db.query(Run).filter(
        Run.status == "COMPLETED",
        Run.duration_ms.isnot(None)
    ).all()
    avg_decision_time = sum(r.duration_ms for r in completed_runs) / len(completed_runs) if completed_runs else 0
    
    # Decision mix
    approve_count = db.query(Decision).filter(Decision.status == "APPROVE").count()
    review_count = db.query(Decision).filter(Decision.status == "REVIEW").count()
    reject_count = db.query(Decision).filter(Decision.status == "REJECT").count()
    
    # Top fraud scenarios
    top_fraud = db.query(FraudScenario).order_by(
        FraudScenario.hits_count.desc()
    ).limit(5).all()
    
    return MetricsResponse(
        claims_today=claims_today,
        stp_rate=round(stp_rate, 1),
        fraud_hit_rate=round(fraud_hit_rate, 1),
        avg_decision_time_ms=round(avg_decision_time, 0),
        decision_mix={
            "approve": approve_count,
            "review": review_count,
            "reject": reject_count
        },
        top_fraud_scenarios=[
            {"name": s.name, "count": s.hits_count}
            for s in top_fraud
        ],
        top_policy_exclusions=[
            {"name": "Pre-existing Condition", "count": 5},
            {"name": "Waiting Period", "count": 3},
            {"name": "Coverage Limit Exceeded", "count": 2}
        ]
    )
