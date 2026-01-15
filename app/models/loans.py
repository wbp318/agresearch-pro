"""
AgResearch Pro - Loan Models
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

class LoanType(str, enum.Enum):
    FSA_OPERATING = "fsa_operating"
    FSA_OWNERSHIP = "fsa_ownership"
    FSA_EMERGENCY = "fsa_emergency"
    FSA_YOUTH = "fsa_youth"
    COMMERCIAL_OPERATING = "commercial_operating"
    COMMERCIAL_REAL_ESTATE = "commercial_real_estate"
    EQUIPMENT = "equipment"
    LINE_OF_CREDIT = "line_of_credit"


class LoanStatus(str, enum.Enum):
    RESEARCHING = "researching"
    APPLYING = "applying"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    ACTIVE = "active"
    PAID_OFF = "paid_off"


# ============================================================================
# SQLALCHEMY MODELS
# ============================================================================

class LoanProgram(Base):
    """Loan programs available"""
    __tablename__ = "loan_programs"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    loan_type = Column(String(50), default=LoanType.COMMERCIAL_OPERATING.value)
    lender = Column(String(200))  # FSA, Bank name, etc.

    # Terms
    min_amount = Column(Float)
    max_amount = Column(Float)
    interest_rate_min = Column(Float)
    interest_rate_max = Column(Float)
    term_months_min = Column(Integer)
    term_months_max = Column(Integer)

    # Requirements
    down_payment_percent = Column(Float, default=0)
    collateral_required = Column(Boolean, default=True)
    eligibility_requirements = Column(Text)

    # FSA specific
    is_fsa = Column(Boolean, default=False)
    fsa_program_code = Column(String(20))

    description = Column(Text)
    website = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)


class LoanApplication(Base):
    """Loan applications"""
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("loan_programs.id"))

    # Application info
    title = Column(String(200))
    status = Column(String(20), default=LoanStatus.RESEARCHING.value)

    # Amounts
    requested_amount = Column(Float)
    approved_amount = Column(Float)

    # Terms
    interest_rate = Column(Float)
    term_months = Column(Integer)
    down_payment = Column(Float, default=0)

    # Dates
    application_date = Column(Date)
    decision_date = Column(Date)
    closing_date = Column(Date)
    first_payment_date = Column(Date)

    # Purpose
    purpose = Column(Text)
    collateral_description = Column(Text)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoanComparison(Base):
    """Saved loan comparisons"""
    __tablename__ = "loan_comparisons"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))

    # Loan parameters
    amount = Column(Float, nullable=False)
    purpose = Column(String(200))

    # Comparison data (JSON)
    comparison_data = Column(Text)  # JSON of compared loan options

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class LoanProgramSchema(BaseModel):
    id: Optional[int] = None
    name: str
    loan_type: LoanType = LoanType.COMMERCIAL_OPERATING
    lender: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    interest_rate_min: Optional[float] = None
    interest_rate_max: Optional[float] = None
    term_months_min: Optional[int] = None
    term_months_max: Optional[int] = None
    down_payment_percent: float = 0
    is_fsa: bool = False
    description: Optional[str] = None

    class Config:
        from_attributes = True


class LoanApplicationSchema(BaseModel):
    id: Optional[int] = None
    program_id: Optional[int] = None
    title: Optional[str] = None
    status: LoanStatus = LoanStatus.RESEARCHING
    requested_amount: Optional[float] = None
    approved_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    term_months: Optional[int] = None
    purpose: Optional[str] = None

    class Config:
        from_attributes = True


class LoanCalculationRequest(BaseModel):
    """Request for loan payment calculation"""
    principal: float
    interest_rate: float  # Annual rate as percentage (e.g., 5.5)
    term_months: int
    down_payment: float = 0


class LoanCalculationResponse(BaseModel):
    """Loan payment calculation results"""
    principal: float
    down_payment: float
    loan_amount: float
    interest_rate: float
    term_months: int
    monthly_payment: float
    total_interest: float
    total_cost: float
