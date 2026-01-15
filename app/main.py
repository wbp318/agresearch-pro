"""
AgResearch Pro - Main Application
Agricultural Grants, Research & Funding Management Platform
"""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

# App configuration
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# Create FastAPI app
app = FastAPI(
    title="AgResearch Pro",
    description="Agricultural Grants, Research & Funding Management Platform",
    version="0.1.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


# ============================================================================
# WEB PAGES (HTML)
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page / Dashboard"""
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "stats": {
                "active_grants": 12,
                "pending_applications": 5,
                "upcoming_deadlines": 3,
                "total_funding": 450000,
            }
        }
    )


@app.get("/grants", response_class=HTMLResponse)
async def grants_page(request: Request):
    """Grant discovery and search page"""
    return templates.TemplateResponse(
        "pages/grants.html",
        {
            "request": request,
            "title": "Grant Discovery",
        }
    )


@app.get("/applications", response_class=HTMLResponse)
async def applications_page(request: Request):
    """Application tracking page"""
    return templates.TemplateResponse(
        "pages/applications.html",
        {
            "request": request,
            "title": "Applications",
        }
    )


@app.get("/research", response_class=HTMLResponse)
async def research_page(request: Request):
    """Research management page"""
    return templates.TemplateResponse(
        "pages/research.html",
        {
            "request": request,
            "title": "Research Projects",
        }
    )


@app.get("/loans", response_class=HTMLResponse)
async def loans_page(request: Request):
    """Loan comparison page"""
    return templates.TemplateResponse(
        "pages/loans.html",
        {
            "request": request,
            "title": "Loan Comparison",
        }
    )


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports and analytics page"""
    return templates.TemplateResponse(
        "pages/reports.html",
        {
            "request": request,
            "title": "Reports",
        }
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "title": "Settings",
        }
    )


# ============================================================================
# API ROUTES (JSON)
# ============================================================================

# Import and include API routers
from app.api import grants, applications, research, loans

app.include_router(grants.router, prefix="/api/v1/grants", tags=["Grants"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(loans.router, prefix="/api/v1/loans", tags=["Loans"])

# AgTools Integration - Powered by AgTools backend services
from app.api import trials, nrcs

app.include_router(trials.router, prefix="/api/v1/trials", tags=["Field Trials (AgTools)"])
app.include_router(nrcs.router, prefix="/api/v1/nrcs", tags=["NRCS & Grants (AgTools)"])


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and load data on startup"""
    from app.models.database import init_db
    await init_db()
    print("AgResearch Pro started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("AgResearch Pro shutting down")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
