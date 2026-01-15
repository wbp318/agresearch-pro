"""
AgTools Integration Layer for AgResearch Pro

Imports and exposes AgTools services for use in AgResearch Pro,
providing access to research trial management, grant support,
sustainability tracking, and more.
"""

import sys
from pathlib import Path

# Add agtools to Python path
# Path: agtools_integration.py -> services -> app -> agresearch-pro -> "Tap Parker Farms" -> agtools
AGTOOLS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "agtools"
if str(AGTOOLS_PATH) not in sys.path:
    sys.path.insert(0, str(AGTOOLS_PATH))

# Import AgTools services
from backend.services.research_service import (
    ResearchService,
    get_research_service,
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
    PlotStatus,
    MeasurementType,
)

from backend.services.grant_service import (
    GrantService,
    get_grant_service,
    GrantProgram,
    NRCSCategory,
    CarbonProgram,
    NRCS_PRACTICES,
    CARBON_PROGRAMS,
    BENCHMARK_DATA,
)


# =============================================================================
# SERVICE FACTORY FUNCTIONS
# =============================================================================

# Use shared database path for AgResearch Pro
AGRESEARCH_DB_PATH = Path(__file__).parent.parent.parent / "data" / "agresearch.db"

_research_service = None
_grant_service = None


def _init_fields_table(db_path: str):
    """Initialize the fields table that research_service depends on"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            farm_id INTEGER,
            acres REAL,
            soil_type VARCHAR(100),
            irrigation_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_agresearch_research_service() -> ResearchService:
    """Get research service configured for AgResearch Pro"""
    global _research_service
    if _research_service is None:
        # Ensure data directory exists
        AGRESEARCH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Initialize fields table (dependency for research_service)
        _init_fields_table(str(AGRESEARCH_DB_PATH))
        _research_service = ResearchService(db_path=str(AGRESEARCH_DB_PATH))
    return _research_service


def get_agresearch_grant_service() -> GrantService:
    """Get grant service for AgResearch Pro"""
    global _grant_service
    if _grant_service is None:
        _grant_service = GrantService()
    return _grant_service


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

__all__ = [
    # Research Service
    "ResearchService",
    "get_agresearch_research_service",
    "TrialCreate",
    "TrialUpdate",
    "TrialResponse",
    "TreatmentCreate",
    "TreatmentResponse",
    "PlotCreate",
    "PlotResponse",
    "MeasurementCreate",
    "MeasurementResponse",
    "TrialAnalysis",
    "ResearchExport",
    "TrialType",
    "ExperimentalDesign",
    "PlotStatus",
    "MeasurementType",

    # Grant Service
    "GrantService",
    "get_agresearch_grant_service",
    "GrantProgram",
    "NRCSCategory",
    "CarbonProgram",
    "NRCS_PRACTICES",
    "CARBON_PROGRAMS",
    "BENCHMARK_DATA",
]
