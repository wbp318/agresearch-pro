"""
AgResearch Pro - Grants API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from datetime import date

from app.models.database import get_db
from app.models.grants import (
    Grant, GrantProgram, GrantCategory,
    GrantSchema, GrantProgramSchema, GrantCategorySchema,
    GrantSearchParams, GrantSource, GrantStatus
)

router = APIRouter()


# ============================================================================
# GRANT CATEGORIES
# ============================================================================

@router.get("/categories", response_model=List[GrantCategorySchema])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all grant categories"""
    result = await db.execute(select(GrantCategory).order_by(GrantCategory.name))
    return result.scalars().all()


@router.get("/categories/{category_id}", response_model=GrantCategorySchema)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific category"""
    result = await db.execute(select(GrantCategory).where(GrantCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# ============================================================================
# GRANT PROGRAMS
# ============================================================================

@router.get("/programs", response_model=List[GrantProgramSchema])
async def list_programs(
    source: Optional[GrantSource] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List grant programs with optional filtering"""
    query = select(GrantProgram)

    if source:
        query = query.where(GrantProgram.source == source.value)
    if category_id:
        query = query.where(GrantProgram.category_id == category_id)

    query = query.order_by(GrantProgram.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/programs/{program_id}", response_model=GrantProgramSchema)
async def get_program(program_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific grant program"""
    result = await db.execute(select(GrantProgram).where(GrantProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


# ============================================================================
# GRANTS
# ============================================================================

@router.get("/", response_model=List[GrantSchema])
async def list_grants(
    status: Optional[GrantStatus] = None,
    program_id: Optional[int] = None,
    bookmarked: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List grants with optional filtering"""
    query = select(Grant)

    if status:
        query = query.where(Grant.status == status.value)
    if program_id:
        query = query.where(Grant.program_id == program_id)
    if bookmarked is not None:
        query = query.where(Grant.is_bookmarked == bookmarked)

    query = query.order_by(Grant.close_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/search")
async def search_grants(
    q: Optional[str] = Query(None, description="Search query"),
    source: Optional[GrantSource] = None,
    min_award: Optional[float] = None,
    max_award: Optional[float] = None,
    deadline_before: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """Search grants"""
    query = select(Grant)

    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Grant.title.ilike(search_term),
                Grant.description.ilike(search_term)
            )
        )

    if min_award:
        query = query.where(Grant.award_floor >= min_award)
    if max_award:
        query = query.where(Grant.award_ceiling <= max_award)
    if deadline_before:
        query = query.where(Grant.close_date <= deadline_before)

    query = query.order_by(Grant.close_date)
    result = await db.execute(query)
    grants = result.scalars().all()

    return {
        "count": len(grants),
        "results": [GrantSchema.model_validate(g) for g in grants]
    }


@router.get("/{grant_id}", response_model=GrantSchema)
async def get_grant(grant_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific grant"""
    result = await db.execute(select(Grant).where(Grant.id == grant_id))
    grant = result.scalar_one_or_none()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant


@router.post("/{grant_id}/bookmark")
async def toggle_bookmark(grant_id: int, db: AsyncSession = Depends(get_db)):
    """Toggle bookmark status for a grant"""
    result = await db.execute(select(Grant).where(Grant.id == grant_id))
    grant = result.scalar_one_or_none()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    grant.is_bookmarked = not grant.is_bookmarked
    await db.commit()

    return {"id": grant_id, "is_bookmarked": grant.is_bookmarked}


# ============================================================================
# UPCOMING DEADLINES
# ============================================================================

@router.get("/deadlines/upcoming")
async def upcoming_deadlines(
    days: int = Query(30, description="Number of days to look ahead"),
    db: AsyncSession = Depends(get_db)
):
    """Get grants with upcoming deadlines"""
    from datetime import timedelta

    today = date.today()
    end_date = today + timedelta(days=days)

    query = select(Grant).where(
        Grant.status == GrantStatus.OPEN.value,
        Grant.close_date >= today,
        Grant.close_date <= end_date
    ).order_by(Grant.close_date)

    result = await db.execute(query)
    grants = result.scalars().all()

    return {
        "period": f"Next {days} days",
        "count": len(grants),
        "deadlines": [
            {
                "id": g.id,
                "title": g.title,
                "close_date": g.close_date.isoformat() if g.close_date else None,
                "days_remaining": (g.close_date - today).days if g.close_date else None
            }
            for g in grants
        ]
    }
