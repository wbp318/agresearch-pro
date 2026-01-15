"""
NRCS Practices & Grant Support API - Powered by AgTools

Provides grant application support including:
- NRCS conservation practice database with official codes
- Carbon credit calculations and program comparisons
- Benchmark comparisons vs regional/national averages
- Grant reporting for SARE, SBIR, CIG, EQIP
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, Field

from app.services.agtools_integration import (
    get_agresearch_grant_service,
    NRCS_PRACTICES,
    CARBON_PROGRAMS,
    BENCHMARK_DATA,
)

router = APIRouter()


# =============================================================================
# REQUEST MODELS
# =============================================================================

class PracticeImplementationRequest(BaseModel):
    """Record implementation of an NRCS practice"""
    practice_code: str = Field(..., description="NRCS practice code (e.g., '340' for Cover Crop)")
    field_id: str = Field(..., description="Field identifier")
    field_name: str = Field(..., description="Field name")
    acres: float = Field(..., gt=0, description="Acres implemented")
    start_date: date = Field(..., description="Implementation start date")
    notes: str = Field("", description="Implementation notes")
    gps_coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates {lat, lon}")


class DocumentationRequest(BaseModel):
    """Add documentation to a practice implementation"""
    implementation_id: str = Field(..., description="Implementation ID")
    document_type: str = Field(..., description="Type of document (e.g., 'Seed receipts', 'Photos')")
    document_path: str = Field(..., description="Path or reference to document")
    document_date: date = Field(..., description="Document date")


class VerificationRequest(BaseModel):
    """Record verification of a practice implementation"""
    implementation_id: str = Field(..., description="Implementation ID")
    verifier: str = Field(..., description="Name of verifier")
    verification_date: date = Field(..., description="Verification date")
    passed: bool = Field(..., description="Whether verification passed")
    notes: str = Field("", description="Verification notes")


class BenchmarkComparisonRequest(BaseModel):
    """Compare farm metrics to benchmarks"""
    metrics: Dict[str, float] = Field(..., description="Farm metrics to compare")
    farm_name: str = Field("Farm", description="Farm name for report")


class SAREReportRequest(BaseModel):
    """Generate SARE grant report"""
    farm_name: str
    project_title: str
    project_description: str
    practices_implemented: List[str] = Field(..., description="List of NRCS practice codes")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Economic and environmental metrics")


class EQIPApplicationRequest(BaseModel):
    """Generate EQIP application data"""
    farm_name: str
    farm_acres: float
    priority_resource_concerns: List[str] = Field(
        ...,
        description="e.g., ['soil_erosion', 'water_quality', 'soil_health']"
    )
    planned_practices: List[str] = Field(..., description="List of NRCS practice codes")


class GrantReadinessRequest(BaseModel):
    """Assess grant readiness"""
    farm_name: str
    farm_acres: float
    years_in_operation: int
    current_practices: List[str] = Field(..., description="Currently implemented practice codes")
    farm_metrics: Dict[str, float] = Field(default_factory=dict, description="Farm performance metrics")
    target_grants: Optional[List[str]] = Field(None, description="Specific grants to assess")


# =============================================================================
# NRCS PRACTICE DATABASE
# =============================================================================

@router.get("/practices")
async def list_nrcs_practices(
    category: Optional[str] = Query(None, description="Filter by category"),
    program: Optional[str] = Query(None, description="Filter by eligible program (EQIP, CSP, etc.)"),
):
    """
    List all NRCS conservation practices.

    Categories: soil_health, water_quality, water_quantity, air_quality, wildlife, energy, plant_health
    Programs: EQIP, CSP, CIG, CRP
    """
    service = get_agresearch_grant_service()

    if program:
        return service.get_practices_by_program(program)

    practices = service.get_all_nrcs_practices()

    if category:
        practices = [p for p in practices if p["category"] == category]

    return practices


@router.get("/practices/{code}")
async def get_practice(code: str):
    """
    Get details for a specific NRCS practice by code.

    Example codes:
    - 340: Cover Crop
    - 329: No-Till
    - 590: Nutrient Management
    - 595: Integrated Pest Management
    - 412: Grassed Waterway
    """
    service = get_agresearch_grant_service()
    result = service.get_practice_by_code(code)
    if not result:
        raise HTTPException(status_code=404, detail=f"Practice code {code} not found")
    return result


# =============================================================================
# PRACTICE IMPLEMENTATION TRACKING
# =============================================================================

@router.post("/implementations")
async def record_implementation(data: PracticeImplementationRequest):
    """
    Record implementation of an NRCS practice on a field.
    This creates a trackable record for grant compliance.
    """
    service = get_agresearch_grant_service()
    result = service.record_practice_implementation(
        practice_code=data.practice_code,
        field_id=data.field_id,
        field_name=data.field_name,
        acres=data.acres,
        start_date=data.start_date,
        notes=data.notes,
        gps_coordinates=data.gps_coordinates,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/implementations/documentation")
async def add_documentation(data: DocumentationRequest):
    """Add documentation to a practice implementation"""
    service = get_agresearch_grant_service()
    result = service.add_practice_documentation(
        implementation_id=data.implementation_id,
        document_type=data.document_type,
        document_path=data.document_path,
        document_date=data.document_date,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/implementations/verify")
async def verify_implementation(data: VerificationRequest):
    """Record verification of a practice implementation"""
    service = get_agresearch_grant_service()
    result = service.verify_practice(
        implementation_id=data.implementation_id,
        verifier=data.verifier,
        verification_date=data.verification_date,
        passed=data.passed,
        notes=data.notes,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/implementations/summary")
async def get_implementation_summary():
    """Get summary of all implemented practices"""
    service = get_agresearch_grant_service()
    return service.get_practice_summary()


# =============================================================================
# CARBON CREDIT CALCULATIONS
# =============================================================================

@router.get("/carbon/programs")
async def list_carbon_programs():
    """
    List available carbon credit programs.

    Includes: Nori, Indigo Carbon, Bayer Carbon, Cargill RegenConnect,
    Corteva, Nutrien, Gradable (ADM), Truterra (Land O'Lakes)
    """
    service = get_agresearch_grant_service()
    return service.get_carbon_programs()


@router.get("/carbon/calculate")
async def calculate_carbon_credits(
    practice_code: str = Query(..., description="NRCS practice code"),
    acres: float = Query(..., gt=0, description="Acres to calculate for"),
    years: int = Query(5, ge=1, le=10, description="Contract duration in years"),
):
    """
    Calculate potential carbon credit revenue for a practice.

    Returns revenue estimates across all eligible carbon programs
    with low/mid/high price scenarios.
    """
    service = get_agresearch_grant_service()
    result = service.calculate_carbon_credits(practice_code, acres, years)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/carbon/portfolio")
async def calculate_carbon_portfolio():
    """
    Calculate total carbon credit potential for all implemented practices.
    Returns best program recommendation and revenue projections.
    """
    service = get_agresearch_grant_service()
    return service.calculate_farm_carbon_portfolio()


# =============================================================================
# BENCHMARK COMPARISONS
# =============================================================================

@router.get("/benchmarks")
async def list_benchmarks():
    """
    List available benchmark metrics.

    Categories:
    - Yield (corn, soybean, rice)
    - Input efficiency (nitrogen, water, pesticides)
    - Sustainability (carbon footprint, organic matter, cover crops)
    - Economic (cost per bushel, profit per acre)
    """
    service = get_agresearch_grant_service()
    return service.get_available_benchmarks()


@router.get("/benchmarks/compare")
async def compare_benchmark(
    metric: str = Query(..., description="Metric to compare"),
    farm_value: float = Query(..., description="Your farm's value for this metric"),
):
    """
    Compare a single farm metric to regional and national benchmarks.

    Returns percentile ranking and interpretation.
    """
    service = get_agresearch_grant_service()
    result = service.compare_to_benchmarks(metric, farm_value)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/benchmarks/report")
async def generate_benchmark_report(data: BenchmarkComparisonRequest):
    """
    Generate comprehensive benchmark comparison report.

    Compares multiple metrics at once, identifies strengths
    and improvement opportunities.
    """
    service = get_agresearch_grant_service()
    return service.generate_benchmark_report(data.metrics, data.farm_name)


# =============================================================================
# GRANT REPORTING
# =============================================================================

@router.post("/reports/sare")
async def generate_sare_report(data: SAREReportRequest):
    """
    Generate report formatted for SARE (Sustainable Agriculture Research & Education) grant application.

    Includes:
    - Project summary
    - Sustainable practices documentation
    - Environmental impact assessment
    - Outreach plan template
    """
    service = get_agresearch_grant_service()
    return service.generate_sare_report(
        farm_name=data.farm_name,
        project_title=data.project_title,
        project_description=data.project_description,
        practices_implemented=data.practices_implemented,
        metrics=data.metrics,
    )


@router.get("/reports/sbir")
async def generate_sbir_metrics(
    product_name: str = Query("AgTools", description="Product name"),
    version: str = Query("3.5.0", description="Version"),
):
    """
    Generate metrics section for SBIR/STTR applications.

    Includes innovation metrics, commercialization data,
    societal benefits, and technical readiness level.
    """
    service = get_agresearch_grant_service()
    return service.generate_sbir_metrics(product_name, version)


@router.post("/reports/eqip")
async def generate_eqip_application(data: EQIPApplicationRequest):
    """
    Generate data package for EQIP (Environmental Quality Incentives Program) application.

    Includes:
    - Resource concern analysis
    - Practice recommendations
    - Payment estimates
    - Required documentation checklist
    """
    service = get_agresearch_grant_service()
    return service.generate_eqip_application_data(
        farm_name=data.farm_name,
        farm_acres=data.farm_acres,
        priority_resource_concerns=data.priority_resource_concerns,
        planned_practices=data.planned_practices,
    )


@router.post("/readiness")
async def assess_grant_readiness(data: GrantReadinessRequest):
    """
    Comprehensive assessment of readiness for various grant programs.

    Evaluates:
    - USDA SBIR
    - SARE Producer Grant
    - Conservation Innovation Grant (CIG)
    - EQIP

    Returns readiness scores, requirements met/missing, and priority actions.
    """
    service = get_agresearch_grant_service()
    return service.assess_grant_readiness(
        farm_name=data.farm_name,
        farm_acres=data.farm_acres,
        years_in_operation=data.years_in_operation,
        current_practices=data.current_practices,
        farm_metrics=data.farm_metrics,
        target_grants=data.target_grants,
    )


# =============================================================================
# REFERENCE DATA
# =============================================================================

@router.get("/reference/categories")
async def get_practice_categories():
    """Get NRCS practice categories"""
    return [
        {"value": "soil_health", "label": "Soil Health"},
        {"value": "water_quality", "label": "Water Quality"},
        {"value": "water_quantity", "label": "Water Quantity"},
        {"value": "air_quality", "label": "Air Quality"},
        {"value": "wildlife", "label": "Wildlife Habitat"},
        {"value": "energy", "label": "Energy"},
        {"value": "plant_health", "label": "Plant Health"},
    ]


@router.get("/reference/programs")
async def get_grant_programs():
    """Get supported grant programs"""
    return [
        {"value": "EQIP", "label": "Environmental Quality Incentives Program", "agency": "NRCS"},
        {"value": "CSP", "label": "Conservation Stewardship Program", "agency": "NRCS"},
        {"value": "CIG", "label": "Conservation Innovation Grant", "agency": "NRCS"},
        {"value": "CRP", "label": "Conservation Reserve Program", "agency": "FSA"},
        {"value": "SARE", "label": "Sustainable Agriculture Research & Education", "agency": "USDA"},
        {"value": "SBIR", "label": "Small Business Innovation Research", "agency": "USDA/NSF"},
    ]


@router.get("/reference/resource-concerns")
async def get_resource_concerns():
    """Get resource concern types for EQIP applications"""
    return [
        {"value": "soil_erosion", "label": "Soil Erosion", "practices": ["340", "329", "330", "412"]},
        {"value": "water_quality", "label": "Water Quality", "practices": ["590", "393", "391", "412"]},
        {"value": "soil_health", "label": "Soil Health", "practices": ["340", "329", "328", "484"]},
        {"value": "wildlife_habitat", "label": "Wildlife Habitat", "practices": ["420", "393", "391"]},
        {"value": "air_quality", "label": "Air Quality", "practices": ["329", "345", "340"]},
    ]
