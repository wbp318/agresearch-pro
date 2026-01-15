"""
Field Trials API - Powered by AgTools

Provides research-grade field trial management including:
- Trial design (CRD, RCBD, split-plot, factorial)
- Treatment and plot management
- Data collection and measurements
- Statistical analysis (t-tests, ANOVA, LSD)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date

from app.services.agtools_integration import (
    get_agresearch_research_service,
    TrialCreate,
    TrialUpdate,
    TrialResponse,
    TreatmentCreate,
    TreatmentResponse,
    PlotCreate,
    PlotResponse,
    MeasurementCreate,
    MeasurementResponse,
    TrialAnalysis,
    ResearchExport,
    TrialType,
    ExperimentalDesign,
    MeasurementType,
)

router = APIRouter()


# =============================================================================
# TRIAL MANAGEMENT
# =============================================================================

@router.get("/", response_model=List[TrialResponse])
async def list_trials(
    year: Optional[int] = Query(None, description="Filter by year"),
    trial_type: Optional[TrialType] = Query(None, description="Filter by trial type"),
    field_id: Optional[int] = Query(None, description="Filter by field"),
):
    """List all research trials with optional filters"""
    service = get_agresearch_research_service()
    return service.list_trials(year=year, trial_type=trial_type, field_id=field_id)


@router.post("/", response_model=TrialResponse)
async def create_trial(data: TrialCreate):
    """
    Create a new field trial.

    Supported trial types:
    - variety_trial: Compare crop varieties
    - treatment_comparison: Compare treatments/products
    - rate_study: Test different application rates
    - timing_study: Test application timing
    - product_evaluation: Evaluate new products
    - demonstration: On-farm demos
    - on_farm_research: Farmer-led research

    Supported experimental designs:
    - completely_randomized (CRD)
    - randomized_complete_block (RCBD)
    - split_plot
    - strip_plot
    - factorial
    - simple_paired (A/B comparison)
    """
    service = get_agresearch_research_service()
    result, error = service.create_trial(data, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/{trial_id}", response_model=TrialResponse)
async def get_trial(trial_id: int):
    """Get a specific trial by ID"""
    service = get_agresearch_research_service()
    result = service.get_trial(trial_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trial not found")
    return result


@router.put("/{trial_id}", response_model=TrialResponse)
async def update_trial(trial_id: int, data: TrialUpdate):
    """Update trial details"""
    service = get_agresearch_research_service()
    result, error = service.update_trial(trial_id, data, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not result:
        raise HTTPException(status_code=404, detail="Trial not found")
    return result


# =============================================================================
# TREATMENT MANAGEMENT
# =============================================================================

@router.get("/{trial_id}/treatments", response_model=List[TreatmentResponse])
async def list_treatments(trial_id: int):
    """List all treatments for a trial"""
    service = get_agresearch_research_service()
    return service.list_treatments(trial_id)


@router.post("/{trial_id}/treatments", response_model=TreatmentResponse)
async def add_treatment(trial_id: int, data: TreatmentCreate):
    """Add a treatment to a trial"""
    # Ensure trial_id matches
    data.trial_id = trial_id
    service = get_agresearch_research_service()
    result, error = service.add_treatment(data, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


# =============================================================================
# PLOT MANAGEMENT
# =============================================================================

@router.get("/{trial_id}/plots", response_model=List[PlotResponse])
async def list_plots(trial_id: int):
    """List all plots for a trial"""
    service = get_agresearch_research_service()
    return service.list_plots(trial_id)


@router.post("/{trial_id}/plots", response_model=PlotResponse)
async def add_plot(trial_id: int, data: PlotCreate):
    """Add a plot to a trial"""
    data.trial_id = trial_id
    service = get_agresearch_research_service()
    result, error = service.add_plot(data, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.post("/{trial_id}/plots/generate")
async def generate_plots(trial_id: int):
    """
    Auto-generate all plots for a trial based on treatments and replications.
    Creates plots for each treatment × replication combination.
    """
    service = get_agresearch_research_service()
    count, error = service.generate_plots(trial_id, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"plots_created": count, "message": f"Generated {count} plots for trial"}


# =============================================================================
# MEASUREMENTS
# =============================================================================

@router.get("/{trial_id}/measurements", response_model=List[MeasurementResponse])
async def list_measurements(
    trial_id: int,
    measurement_type: Optional[MeasurementType] = Query(None, description="Filter by measurement type"),
    plot_id: Optional[int] = Query(None, description="Filter by plot"),
):
    """List all measurements for a trial"""
    service = get_agresearch_research_service()
    return service.list_measurements(trial_id, measurement_type=measurement_type, plot_id=plot_id)


@router.post("/measurements", response_model=MeasurementResponse)
async def record_measurement(data: MeasurementCreate):
    """
    Record a measurement for a plot.

    Measurement types:
    - yield: Crop yield (bu/acre, lbs/acre)
    - plant_population: Plants per acre
    - plant_height: Height in inches
    - pest_rating: Pest severity (0-10)
    - disease_rating: Disease severity (0-10)
    - vigor_rating: Plant vigor (1-10)
    - moisture: Grain moisture %
    - test_weight: Test weight (lbs/bu)
    - lodging: % lodging
    - greensnap: % greensnap
    - standability: Standability rating
    - custom: Custom measurement (specify custom_name)
    """
    service = get_agresearch_research_service()
    result, error = service.record_measurement(data, user_id=1)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

@router.get("/{trial_id}/analysis", response_model=TrialAnalysis)
async def analyze_trial(
    trial_id: int,
    measurement_type: MeasurementType = Query(..., description="Measurement type to analyze"),
):
    """
    Perform statistical analysis on trial data.

    Returns:
    - Treatment means with standard deviations
    - Pairwise t-tests between treatments
    - LSD values at 0.05 and 0.01 significance levels
    - Interpretation and top performer identification
    """
    service = get_agresearch_research_service()
    result = service.analyze_trial(trial_id, measurement_type)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No data available for analysis. Ensure measurements have been recorded."
        )
    return result


# =============================================================================
# DATA EXPORT
# =============================================================================

@router.get("/{trial_id}/export", response_model=ResearchExport)
async def export_trial(
    trial_id: int,
    include_analysis: bool = Query(True, description="Include statistical analysis"),
):
    """
    Export complete trial data for research documentation.

    Includes:
    - Trial details and protocol
    - All treatments and plots
    - All measurements
    - Statistical analysis (optional)
    """
    service = get_agresearch_research_service()
    result = service.export_trial_data(trial_id, include_analysis=include_analysis)
    if not result:
        raise HTTPException(status_code=404, detail="Trial not found")
    return result


# =============================================================================
# REFERENCE DATA
# =============================================================================

@router.get("/reference/trial-types")
async def get_trial_types():
    """Get available trial types"""
    return [
        {"value": t.value, "label": t.value.replace("_", " ").title()}
        for t in TrialType
    ]


@router.get("/reference/experimental-designs")
async def get_experimental_designs():
    """Get available experimental designs with descriptions"""
    designs = {
        "completely_randomized": "CRD - Simple design, treatments randomly assigned",
        "randomized_complete_block": "RCBD - Blocks account for field variability",
        "split_plot": "Main plots and subplots for multi-factor studies",
        "strip_plot": "Horizontal and vertical strips for equipment trials",
        "factorial": "All combinations of two or more factors",
        "simple_paired": "Simple A/B comparison at multiple locations",
    }
    return [
        {"value": d.value, "label": d.value.replace("_", " ").title(), "description": designs.get(d.value, "")}
        for d in ExperimentalDesign
    ]


@router.get("/reference/measurement-types")
async def get_measurement_types():
    """Get available measurement types"""
    return [
        {"value": m.value, "label": m.value.replace("_", " ").title()}
        for m in MeasurementType
    ]
