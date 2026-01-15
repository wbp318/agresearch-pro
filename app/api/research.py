"""
AgResearch Pro - Research API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.database import get_db
from app.models.research import (
    ResearchProject, ResearchProtocol, DataCollection, ResearchReport,
    ResearchProjectSchema, ResearchProtocolSchema, DataCollectionSchema,
    ProjectStatus
)

router = APIRouter()


# ============================================================================
# RESEARCH PROJECTS
# ============================================================================

@router.get("/projects", response_model=List[ResearchProjectSchema])
async def list_projects(
    status: Optional[ProjectStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all research projects"""
    query = select(ResearchProject)
    if status:
        query = query.where(ResearchProject.status == status.value)
    query = query.order_by(ResearchProject.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/projects", response_model=ResearchProjectSchema)
async def create_project(
    project_data: ResearchProjectSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new research project"""
    project = ResearchProject(**project_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=ResearchProjectSchema)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific project"""
    result = await db.execute(select(ResearchProject).where(ResearchProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ResearchProjectSchema)
async def update_project(
    project_id: int,
    project_data: ResearchProjectSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    result = await db.execute(select(ResearchProject).where(ResearchProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project_data.model_dump(exclude_unset=True, exclude={"id"}).items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    return project


# ============================================================================
# PROTOCOLS
# ============================================================================

@router.get("/projects/{project_id}/protocols", response_model=List[ResearchProtocolSchema])
async def list_protocols(project_id: int, db: AsyncSession = Depends(get_db)):
    """List protocols for a project"""
    query = select(ResearchProtocol).where(ResearchProtocol.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/projects/{project_id}/protocols", response_model=ResearchProtocolSchema)
async def create_protocol(
    project_id: int,
    protocol_data: ResearchProtocolSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a protocol for a project"""
    protocol_data.project_id = project_id
    protocol = ResearchProtocol(**protocol_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(protocol)
    await db.commit()
    await db.refresh(protocol)
    return protocol


@router.get("/protocols/{protocol_id}", response_model=ResearchProtocolSchema)
async def get_protocol(protocol_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific protocol"""
    result = await db.execute(select(ResearchProtocol).where(ResearchProtocol.id == protocol_id))
    protocol = result.scalar_one_or_none()
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


# ============================================================================
# DATA COLLECTION
# ============================================================================

@router.get("/projects/{project_id}/data", response_model=List[DataCollectionSchema])
async def list_data(project_id: int, db: AsyncSession = Depends(get_db)):
    """List data collections for a project"""
    query = select(DataCollection).where(
        DataCollection.project_id == project_id
    ).order_by(DataCollection.collection_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/projects/{project_id}/data", response_model=DataCollectionSchema)
async def add_data(
    project_id: int,
    data: DataCollectionSchema,
    db: AsyncSession = Depends(get_db)
):
    """Add a data collection record"""
    data.project_id = project_id
    record = DataCollection(**data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.post("/projects/{project_id}/data/bulk")
async def bulk_add_data(
    project_id: int,
    data_list: List[DataCollectionSchema],
    db: AsyncSession = Depends(get_db)
):
    """Bulk add data collection records"""
    records = []
    for data in data_list:
        data.project_id = project_id
        record = DataCollection(**data.model_dump(exclude_unset=True, exclude={"id"}))
        db.add(record)
        records.append(record)

    await db.commit()
    return {"message": f"Added {len(records)} records"}


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/projects/{project_id}/stats")
async def project_stats(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get statistics for a project"""
    from sqlalchemy import func

    # Protocol count
    result = await db.execute(
        select(func.count(ResearchProtocol.id))
        .where(ResearchProtocol.project_id == project_id)
    )
    protocol_count = result.scalar() or 0

    # Data point count
    result = await db.execute(
        select(func.count(DataCollection.id))
        .where(DataCollection.project_id == project_id)
    )
    data_count = result.scalar() or 0

    # Report count
    result = await db.execute(
        select(func.count(ResearchReport.id))
        .where(ResearchReport.project_id == project_id)
    )
    report_count = result.scalar() or 0

    return {
        "project_id": project_id,
        "protocols": protocol_count,
        "data_points": data_count,
        "reports": report_count
    }
