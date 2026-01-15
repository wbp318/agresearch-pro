# Changelog

All notable changes to AgResearch Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-01-15

### Added - AgTools Integration

Major integration with AgTools backend services, bringing research-grade field trial management and comprehensive grant support to AgResearch Pro.

#### Field Trials API (`/api/v1/trials`)
- **Trial Management**: Create, update, and list research trials
- **7 Trial Types**: variety_trial, treatment_comparison, rate_study, timing_study, product_evaluation, demonstration, on_farm_research
- **5 Experimental Designs**: CRD, RCBD, split-plot, strip-plot, factorial
- **Treatment Management**: Add treatments with product details, rates, and application methods
- **Plot Management**: Manual plot creation or auto-generation based on treatments × replications
- **Measurements**: Record yield, plant population, height, pest/disease ratings, moisture, test weight, and custom measurements
- **Statistical Analysis**: Treatment means, t-tests, LSD at 0.05/0.01 levels, top performer identification
- **Data Export**: Complete trial export with all treatments, plots, measurements, and analysis

#### NRCS & Grants API (`/api/v1/nrcs`)
- **15 NRCS Conservation Practices**: Cover Crop (340), No-Till (329), Nutrient Management (590), IPM (595), and more
- **Practice Implementation Tracking**: Record implementations with acres, dates, GPS coordinates
- **Documentation Management**: Track required documents for each practice
- **Verification Workflow**: Record practice verification for grant compliance
- **8 Carbon Credit Programs**: Nori, Indigo, Bayer, Cargill, Corteva, Nutrien, Gradable, Truterra
- **Carbon Calculations**: Revenue projections with low/mid/high price scenarios
- **Benchmark Comparisons**: Compare farm metrics to Louisiana, Delta region, and national averages
- **Grant Reports**: SARE, SBIR/STTR, EQIP, CIG report generators
- **Readiness Assessment**: Multi-program grant readiness scoring with requirements checklist

#### New Files
- `app/services/agtools_integration.py` - AgTools service import layer
- `app/api/trials.py` - Field trials API (15 endpoints)
- `app/api/nrcs.py` - NRCS practices and grant support API (20 endpoints)

### Changed
- Updated README.md with AgTools features documentation
- Updated README.md with new API endpoint tables
- Updated project structure to reflect new services

---

## [0.1.0] - 2026-01-15

### Added - Initial Release
- **Core Platform**: FastAPI backend with Jinja2 templates
- **Grant Discovery**: Search and filter grant opportunities
- **Application Management**: Track deadlines and documents
- **Research Management**: Basic research project tracking
- **Loan Comparison**: FSA and commercial loan analysis
- **Reports**: Basic reporting functionality
- **Web UI**: HTMX + Alpine.js + Tailwind CSS frontend

#### API Endpoints
- `/api/v1/grants` - Grant discovery and search
- `/api/v1/applications` - Application tracking
- `/api/v1/research` - Research project management
- `/api/v1/loans` - Loan comparison tools

#### Pages
- Dashboard (`/`)
- Grant Discovery (`/grants`)
- Applications (`/applications`)
- Research Projects (`/research`)
- Loan Comparison (`/loans`)
- Reports (`/reports`)
- Settings (`/settings`)

---

## Roadmap

### Planned Features
- [ ] User authentication and multi-tenant support
- [ ] PDF report generation
- [ ] Email notifications for deadlines
- [ ] Document upload and storage
- [ ] Grant application wizard
- [ ] Budget builder with templates
- [ ] Integration with grants.gov API
- [ ] Mobile-responsive UI improvements

---

**Copyright 2026 New Generation Farms. All Rights Reserved.**
