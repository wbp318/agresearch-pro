"""
AgResearch Pro - Grant Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
import enum

from app.models.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class GrantSource(str, enum.Enum):
    FEDERAL = "federal"
    STATE = "state"
    PRIVATE = "private"
    FOUNDATION = "foundation"
    CORPORATE = "corporate"


class GrantStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"
    ROLLING = "rolling"


class EligibilityType(str, enum.Enum):
    FARMER = "farmer"
    BEGINNING_FARMER = "beginning_farmer"
    VETERAN = "veteran"
    SOCIALLY_DISADVANTAGED = "socially_disadvantaged"
    RESEARCHER = "researcher"
    NONPROFIT = "nonprofit"
    COOPERATIVE = "cooperative"
    TRIBAL = "tribal"
    ANY = "any"


# ============================================================================
# SQLALCHEMY MODELS
# ============================================================================

class GrantCategory(Base):
    """Grant categories (Conservation, Research, Equipment, etc.)"""
    __tablename__ = "grant_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))  # Icon name for UI

    # Relationships
    programs = relationship("GrantProgram", back_populates="category")


class GrantProgram(Base):
    """Grant programs (EQIP, SARE, Beginning Farmer, etc.)"""
    __tablename__ = "grant_programs"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    acronym = Column(String(20))
    description = Column(Text)
    source = Column(String(20), default=GrantSource.FEDERAL.value)
    agency = Column(String(100))  # USDA, NRCS, NIFA, etc.
    website = Column(String(500))

    # Category
    category_id = Column(Integer, ForeignKey("grant_categories.id"))
    category = relationship("GrantCategory", back_populates="programs")

    # Funding details
    min_award = Column(Float, default=0)
    max_award = Column(Float)
    typical_award = Column(Float)
    match_required = Column(Boolean, default=False)
    match_percent = Column(Float, default=0)

    # Eligibility
    eligibility_types = Column(Text)  # JSON list of EligibilityType values
    eligibility_notes = Column(Text)
    state_restrictions = Column(Text)  # JSON list of state codes, empty = all states

    # Relationships
    grants = relationship("Grant", back_populates="program")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Grant(Base):
    """Individual grant opportunities"""
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("grant_programs.id"))
    program = relationship("GrantProgram", back_populates="grants")

    # Grant details
    title = Column(String(300), nullable=False)
    description = Column(Text)
    funding_opportunity_number = Column(String(50))  # FON for federal grants
    cfda_number = Column(String(20))  # Catalog of Federal Domestic Assistance

    # Dates
    open_date = Column(Date)
    close_date = Column(Date)
    status = Column(String(20), default=GrantStatus.OPEN.value)

    # Funding
    total_funding = Column(Float)
    expected_awards = Column(Integer)
    award_ceiling = Column(Float)
    award_floor = Column(Float)

    # Application info
    application_url = Column(String(500))
    contact_name = Column(String(100))
    contact_email = Column(String(200))
    contact_phone = Column(String(20))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_bookmarked = Column(Boolean, default=False)
    notes = Column(Text)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class GrantCategorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class GrantProgramSchema(BaseModel):
    id: Optional[int] = None
    name: str
    acronym: Optional[str] = None
    description: Optional[str] = None
    source: GrantSource = GrantSource.FEDERAL
    agency: Optional[str] = None
    website: Optional[str] = None
    category_id: Optional[int] = None
    min_award: float = 0
    max_award: Optional[float] = None
    typical_award: Optional[float] = None
    match_required: bool = False
    match_percent: float = 0

    class Config:
        from_attributes = True


class GrantSchema(BaseModel):
    id: Optional[int] = None
    program_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    funding_opportunity_number: Optional[str] = None
    cfda_number: Optional[str] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    status: GrantStatus = GrantStatus.OPEN
    total_funding: Optional[float] = None
    expected_awards: Optional[int] = None
    award_ceiling: Optional[float] = None
    award_floor: Optional[float] = None
    application_url: Optional[str] = None
    is_bookmarked: bool = False

    class Config:
        from_attributes = True


class GrantSearchParams(BaseModel):
    """Parameters for searching grants"""
    query: Optional[str] = None
    source: Optional[GrantSource] = None
    category_id: Optional[int] = None
    status: Optional[GrantStatus] = None
    min_award: Optional[float] = None
    max_award: Optional[float] = None
    eligibility: Optional[EligibilityType] = None
    state: Optional[str] = None
    deadline_before: Optional[date] = None
    deadline_after: Optional[date] = None
