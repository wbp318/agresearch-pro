"""
AgResearch Pro - Loans API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.database import get_db
from app.models.loans import (
    LoanProgram, LoanApplication, LoanComparison,
    LoanProgramSchema, LoanApplicationSchema,
    LoanCalculationRequest, LoanCalculationResponse,
    LoanType, LoanStatus
)

router = APIRouter()


# ============================================================================
# LOAN PROGRAMS
# ============================================================================

@router.get("/programs", response_model=List[LoanProgramSchema])
async def list_programs(
    loan_type: Optional[LoanType] = None,
    fsa_only: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List available loan programs"""
    query = select(LoanProgram)

    if loan_type:
        query = query.where(LoanProgram.loan_type == loan_type.value)
    if fsa_only is not None:
        query = query.where(LoanProgram.is_fsa == fsa_only)

    query = query.order_by(LoanProgram.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/programs/{program_id}", response_model=LoanProgramSchema)
async def get_program(program_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific loan program"""
    result = await db.execute(select(LoanProgram).where(LoanProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Loan program not found")
    return program


# ============================================================================
# LOAN APPLICATIONS
# ============================================================================

@router.get("/applications", response_model=List[LoanApplicationSchema])
async def list_applications(
    status: Optional[LoanStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List loan applications"""
    query = select(LoanApplication)
    if status:
        query = query.where(LoanApplication.status == status.value)
    query = query.order_by(LoanApplication.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/applications", response_model=LoanApplicationSchema)
async def create_application(
    app_data: LoanApplicationSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a loan application"""
    application = LoanApplication(**app_data.model_dump(exclude_unset=True, exclude={"id"}))
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/applications/{app_id}", response_model=LoanApplicationSchema)
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific loan application"""
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return application


@router.put("/applications/{app_id}", response_model=LoanApplicationSchema)
async def update_application(
    app_id: int,
    app_data: LoanApplicationSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a loan application"""
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    for key, value in app_data.model_dump(exclude_unset=True, exclude={"id"}).items():
        setattr(application, key, value)

    await db.commit()
    await db.refresh(application)
    return application


# ============================================================================
# LOAN CALCULATOR
# ============================================================================

@router.post("/calculate", response_model=LoanCalculationResponse)
async def calculate_loan(request: LoanCalculationRequest):
    """Calculate loan payment details"""
    loan_amount = request.principal - request.down_payment
    monthly_rate = (request.interest_rate / 100) / 12

    if monthly_rate > 0:
        # Standard amortization formula
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** request.term_months
        ) / (
            (1 + monthly_rate) ** request.term_months - 1
        )
    else:
        # Zero interest
        monthly_payment = loan_amount / request.term_months

    total_payments = monthly_payment * request.term_months
    total_interest = total_payments - loan_amount

    return LoanCalculationResponse(
        principal=request.principal,
        down_payment=request.down_payment,
        loan_amount=loan_amount,
        interest_rate=request.interest_rate,
        term_months=request.term_months,
        monthly_payment=round(monthly_payment, 2),
        total_interest=round(total_interest, 2),
        total_cost=round(total_payments + request.down_payment, 2)
    )


@router.post("/compare")
async def compare_loans(requests: List[LoanCalculationRequest]):
    """Compare multiple loan scenarios"""
    results = []
    for req in requests:
        loan_amount = req.principal - req.down_payment
        monthly_rate = (req.interest_rate / 100) / 12

        if monthly_rate > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** req.term_months
            ) / (
                (1 + monthly_rate) ** req.term_months - 1
            )
        else:
            monthly_payment = loan_amount / req.term_months

        total_payments = monthly_payment * req.term_months
        total_interest = total_payments - loan_amount

        results.append({
            "principal": req.principal,
            "down_payment": req.down_payment,
            "loan_amount": loan_amount,
            "interest_rate": req.interest_rate,
            "term_months": req.term_months,
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_cost": round(total_payments + req.down_payment, 2)
        })

    # Sort by total cost
    results.sort(key=lambda x: x["total_cost"])

    return {
        "count": len(results),
        "best_option": results[0] if results else None,
        "all_options": results
    }


# ============================================================================
# FSA LOAN PROGRAMS (Seed Data)
# ============================================================================

@router.get("/fsa/programs")
async def get_fsa_programs():
    """Get current FSA loan program details"""
    return {
        "programs": [
            {
                "name": "FSA Direct Operating Loan",
                "code": "OL",
                "max_amount": 400000,
                "interest_rate": "Current rate set quarterly",
                "term_years": "1-7 years",
                "use": "Annual operating expenses, equipment, livestock, farm improvements",
                "eligibility": "Beginning farmer or unable to obtain commercial credit"
            },
            {
                "name": "FSA Direct Farm Ownership Loan",
                "code": "FO",
                "max_amount": 600000,
                "interest_rate": "Current rate set quarterly",
                "term_years": "Up to 40 years",
                "use": "Purchase farmland, construct/improve buildings, soil/water conservation",
                "eligibility": "Beginning farmer or unable to obtain commercial credit"
            },
            {
                "name": "FSA Guaranteed Operating Loan",
                "code": "GOL",
                "max_amount": 1750000,
                "interest_rate": "Negotiated with lender",
                "term_years": "1-7 years",
                "use": "Same as direct operating",
                "eligibility": "Work with approved lender, FSA guarantees 90-95%"
            },
            {
                "name": "FSA Guaranteed Farm Ownership Loan",
                "code": "GFO",
                "max_amount": 1750000,
                "interest_rate": "Negotiated with lender",
                "term_years": "Up to 40 years",
                "use": "Same as direct ownership",
                "eligibility": "Work with approved lender, FSA guarantees 90-95%"
            },
            {
                "name": "FSA Emergency Loan",
                "code": "EM",
                "max_amount": 500000,
                "interest_rate": "Current rate set quarterly",
                "term_years": "1-7 years (operating), up to 40 years (real estate)",
                "use": "Recovery from natural disaster in declared counties",
                "eligibility": "Located in disaster-declared county, suffered 30%+ loss"
            },
            {
                "name": "FSA Youth Loan",
                "code": "YL",
                "max_amount": 5000,
                "interest_rate": "Current rate set quarterly",
                "term_years": "1-7 years",
                "use": "Agricultural project (4-H, FFA)",
                "eligibility": "Ages 10-20, member of 4-H/FFA or similar"
            }
        ],
        "note": "Rates updated quarterly. Contact local FSA office for current rates.",
        "website": "https://www.fsa.usda.gov/programs-and-services/farm-loan-programs/"
    }
