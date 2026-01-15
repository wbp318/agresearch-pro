"""
AgResearch Pro - Application Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
import enum

from app.models.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"


class DocumentType(str, enum.Enum):
    BUDGET = "budget"
    NARRATIVE = "narrative"
    RESUME = "resume"
    LETTERS_OF_SUPPORT = "letters_of_support"
    FINANCIAL_STATEMENTS = "financial_statements"
    PROJECT_PLAN = "project_plan"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"
    OTHER = "other"


# ============================================================================
# SQLALCHEMY MODELS
# ============================================================================

class Application(Base):
    """Grant applications"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    grant_id = Column(Integer, ForeignKey("grants.id"))

    # Application info
    title = Column(String(300), nullable=False)
    status = Column(String(20), default=ApplicationStatus.DRAFT.value)

    # Key dates
    started_date = Column(Date, default=date.today)
    submitted_date = Column(Date)
    decision_date = Column(Date)

    # Funding
    requested_amount = Column(Float)
    awarded_amount = Column(Float)
    match_amount = Column(Float, default=0)

    # Project details
    project_start_date = Column(Date)
    project_end_date = Column(Date)
    project_summary = Column(Text)

    # Tracking
    assigned_to = Column(String(100))  # Team member responsible
    priority = Column(Integer, default=2)  # 1=High, 2=Medium, 3=Low
    notes = Column(Text)

    # Relationships
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    tasks = relationship("ApplicationTask", back_populates="application", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationDocument(Base):
    """Documents attached to applications"""
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    application = relationship("Application", back_populates="documents")

    name = Column(String(200), nullable=False)
    document_type = Column(String(50), default=DocumentType.OTHER.value)
    file_path = Column(String(500))
    file_size = Column(Integer)

    # Status
    is_required = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=False)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationTask(Base):
    """Tasks/checklist items for applications"""
    __tablename__ = "application_tasks"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    application = relationship("Application", back_populates="tasks")

    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    is_complete = Column(Boolean, default=False)
    completed_date = Column(Date)
    assigned_to = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ApplicationSchema(BaseModel):
    id: Optional[int] = None
    grant_id: Optional[int] = None
    title: str
    status: ApplicationStatus = ApplicationStatus.DRAFT
    requested_amount: Optional[float] = None
    awarded_amount: Optional[float] = None
    match_amount: float = 0
    project_summary: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: int = 2

    class Config:
        from_attributes = True


class ApplicationDocumentSchema(BaseModel):
    id: Optional[int] = None
    application_id: Optional[int] = None
    name: str
    document_type: DocumentType = DocumentType.OTHER
    is_required: bool = False
    is_complete: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationTaskSchema(BaseModel):
    id: Optional[int] = None
    application_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_complete: bool = False
    assigned_to: Optional[str] = None

    class Config:
        from_attributes = True
