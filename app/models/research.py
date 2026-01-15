"""
AgResearch Pro - Research Project Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
import enum

from app.models.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class TrialDesign(str, enum.Enum):
    RANDOMIZED_COMPLETE_BLOCK = "rcbd"
    SPLIT_PLOT = "split_plot"
    STRIP_PLOT = "strip_plot"
    LATIN_SQUARE = "latin_square"
    COMPLETELY_RANDOMIZED = "crd"
    FACTORIAL = "factorial"
    ON_FARM_STRIP_TRIAL = "strip_trial"


# ============================================================================
# SQLALCHEMY MODELS
# ============================================================================

class ResearchProject(Base):
    """Research projects"""
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    # Project info
    title = Column(String(300), nullable=False)
    description = Column(Text)
    status = Column(String(20), default=ProjectStatus.PLANNING.value)

    # Principal investigator
    pi_name = Column(String(100))
    pi_email = Column(String(200))
    pi_organization = Column(String(200))

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)

    # Research details
    objectives = Column(Text)
    hypothesis = Column(Text)
    methodology = Column(Text)
    expected_outcomes = Column(Text)

    # Location
    location_description = Column(Text)
    coordinates = Column(String(100))  # lat,lng

    # Relationships
    protocols = relationship("ResearchProtocol", back_populates="project", cascade="all, delete-orphan")
    data_collections = relationship("DataCollection", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("ResearchReport", back_populates="project", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchProtocol(Base):
    """Research protocols/trial designs"""
    __tablename__ = "research_protocols"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="protocols")

    title = Column(String(200), nullable=False)
    trial_design = Column(String(50), default=TrialDesign.RANDOMIZED_COMPLETE_BLOCK.value)

    # Treatments
    treatments = Column(Text)  # JSON array of treatment descriptions
    num_treatments = Column(Integer)
    num_replications = Column(Integer)

    # Plot details
    plot_size = Column(String(50))  # e.g., "30ft x 100ft"
    plot_area = Column(Float)  # acres
    buffer_size = Column(String(50))

    # Data collection plan
    variables_measured = Column(Text)  # JSON array
    measurement_frequency = Column(String(100))
    equipment_needed = Column(Text)

    # Standard operating procedures
    sop = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataCollection(Base):
    """Data collection records"""
    __tablename__ = "data_collections"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="data_collections")
    protocol_id = Column(Integer, ForeignKey("research_protocols.id"))

    # Collection info
    collection_date = Column(Date, nullable=False)
    collector_name = Column(String(100))

    # Data
    treatment_id = Column(String(50))
    replication = Column(Integer)
    variable_name = Column(String(100))
    value = Column(Float)
    unit = Column(String(50))
    notes = Column(Text)

    # Quality
    is_validated = Column(Boolean, default=False)
    validated_by = Column(String(100))
    validation_date = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)


class ResearchReport(Base):
    """Research progress and final reports"""
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="reports")

    title = Column(String(200), nullable=False)
    report_type = Column(String(50))  # progress, annual, final
    report_date = Column(Date)
    due_date = Column(Date)

    # Content
    summary = Column(Text)
    methods_update = Column(Text)
    results = Column(Text)
    conclusions = Column(Text)
    next_steps = Column(Text)

    # Submission
    is_submitted = Column(Boolean, default=False)
    submitted_date = Column(Date)
    file_path = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ResearchProjectSchema(BaseModel):
    id: Optional[int] = None
    application_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    pi_name: Optional[str] = None
    pi_email: Optional[str] = None
    pi_organization: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    objectives: Optional[str] = None

    class Config:
        from_attributes = True


class ResearchProtocolSchema(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    title: str
    trial_design: TrialDesign = TrialDesign.RANDOMIZED_COMPLETE_BLOCK
    num_treatments: Optional[int] = None
    num_replications: Optional[int] = None
    plot_size: Optional[str] = None
    variables_measured: Optional[str] = None

    class Config:
        from_attributes = True


class DataCollectionSchema(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    protocol_id: Optional[int] = None
    collection_date: date
    collector_name: Optional[str] = None
    treatment_id: Optional[str] = None
    replication: Optional[int] = None
    variable_name: str
    value: float
    unit: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
