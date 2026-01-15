"""
AgResearch Pro - Applications API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.database import get_db
from app.models.applications import (
    Application, ApplicationDocument, ApplicationTask,
    ApplicationSchema, ApplicationDocumentSchema, ApplicationTaskSchema,
    ApplicationStatus
)

router = APIRouter()


# ============================================================================
# APPLICATIONS
# ============================================================================

@router.get("/", response_model=List[ApplicationSchema])
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all applications"""
    query = select(Application)
    if status:
        query = query.where(Application.status == status.value)
    query = query.order_by(Application.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ApplicationSchema)
async def create_application(
    app_data: ApplicationSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new application"""
    application = Application(**app_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/{app_id}", response_model=ApplicationSchema)
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific application"""
    result = await db.execute(select(Application).where(Application.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/{app_id}", response_model=ApplicationSchema)
async def update_application(
    app_id: int,
    app_data: ApplicationSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update an application"""
    result = await db.execute(select(Application).where(Application.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for key, value in app_data.model_dump(exclude_unset=True, exclude={"id"}).items():
        setattr(application, key, value)

    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{app_id}")
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an application"""
    result = await db.execute(select(Application).where(Application.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(application)
    await db.commit()
    return {"message": "Application deleted"}


# ============================================================================
# APPLICATION DOCUMENTS
# ============================================================================

@router.get("/{app_id}/documents", response_model=List[ApplicationDocumentSchema])
async def list_documents(app_id: int, db: AsyncSession = Depends(get_db)):
    """List documents for an application"""
    query = select(ApplicationDocument).where(ApplicationDocument.application_id == app_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{app_id}/documents", response_model=ApplicationDocumentSchema)
async def add_document(
    app_id: int,
    doc_data: ApplicationDocumentSchema,
    db: AsyncSession = Depends(get_db)
):
    """Add a document to an application"""
    doc_data.application_id = app_id
    document = ApplicationDocument(**doc_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


@router.put("/{app_id}/documents/{doc_id}", response_model=ApplicationDocumentSchema)
async def update_document(
    app_id: int,
    doc_id: int,
    doc_data: ApplicationDocumentSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a document"""
    result = await db.execute(
        select(ApplicationDocument).where(
            ApplicationDocument.id == doc_id,
            ApplicationDocument.application_id == app_id
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    for key, value in doc_data.model_dump(exclude_unset=True, exclude={"id", "application_id"}).items():
        setattr(document, key, value)

    await db.commit()
    await db.refresh(document)
    return document


# ============================================================================
# APPLICATION TASKS
# ============================================================================

@router.get("/{app_id}/tasks", response_model=List[ApplicationTaskSchema])
async def list_tasks(app_id: int, db: AsyncSession = Depends(get_db)):
    """List tasks for an application"""
    query = select(ApplicationTask).where(
        ApplicationTask.application_id == app_id
    ).order_by(ApplicationTask.due_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{app_id}/tasks", response_model=ApplicationTaskSchema)
async def add_task(
    app_id: int,
    task_data: ApplicationTaskSchema,
    db: AsyncSession = Depends(get_db)
):
    """Add a task to an application"""
    task_data.application_id = app_id
    task = ApplicationTask(**task_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/{app_id}/tasks/{task_id}/complete")
async def complete_task(
    app_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as complete"""
    from datetime import date

    result = await db.execute(
        select(ApplicationTask).where(
            ApplicationTask.id == task_id,
            ApplicationTask.application_id == app_id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_complete = True
    task.completed_date = date.today()
    await db.commit()

    return {"message": "Task marked complete"}


# ============================================================================
# DASHBOARD STATS
# ============================================================================

@router.get("/stats/summary")
async def application_stats(db: AsyncSession = Depends(get_db)):
    """Get application statistics"""
    from sqlalchemy import func

    # Count by status
    result = await db.execute(
        select(Application.status, func.count(Application.id))
        .group_by(Application.status)
    )
    status_counts = dict(result.all())

    # Total funding
    result = await db.execute(
        select(func.sum(Application.awarded_amount))
        .where(Application.status == ApplicationStatus.APPROVED.value)
    )
    total_awarded = result.scalar() or 0

    return {
        "total_applications": sum(status_counts.values()),
        "by_status": status_counts,
        "total_awarded": total_awarded
    }
