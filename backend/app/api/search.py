"""Search API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.models.database import get_db
from app.models.orm import Claim, Run
from app.models.schemas import SearchResult, SearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Global search across claims, customers, and runs."""
    results: List[SearchResult] = []
    search_term = f"%{q.lower()}%"
    
    # Search claims by claim_number, customer_name, customer_email
    claims = db.query(Claim).filter(
        or_(
            Claim.claim_number.ilike(search_term),
            Claim.customer_name.ilike(search_term),
            Claim.customer_email.ilike(search_term),
            Claim.policy_number.ilike(search_term),
            Claim.description.ilike(search_term),
        )
    ).limit(limit).all()
    
    for claim in claims:
        results.append(SearchResult(
            type="claim",
            id=str(claim.id),
            title=claim.claim_number,
            subtitle=f"{claim.customer_name} - ${claim.amount:,.2f}"
        ))
    
    # Search for unique customers
    seen_customers = set()
    for claim in claims:
        if claim.customer_name.lower() not in seen_customers:
            seen_customers.add(claim.customer_name.lower())
            if q.lower() in claim.customer_name.lower():
                results.append(SearchResult(
                    type="customer",
                    id=str(claim.id),
                    title=claim.customer_name,
                    subtitle=claim.customer_email or "No email"
                ))
    
    # Search runs by trace_id
    runs = db.query(Run).filter(
        or_(
            Run.trace_id.ilike(search_term),
            Run.status.ilike(search_term),
        )
    ).limit(limit // 2).all()
    
    for run in runs:
        results.append(SearchResult(
            type="run",
            id=str(run.id),
            title=f"Run {str(run.id)[:8]}...",
            subtitle=f"Status: {run.status} - {run.provider or 'unknown'}"
        ))
    
    # Deduplicate and limit results
    unique_results = []
    seen = set()
    for r in results:
        key = f"{r.type}-{r.id}"
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
            if len(unique_results) >= limit:
                break
    
    return SearchResponse(results=unique_results, total=len(unique_results))
