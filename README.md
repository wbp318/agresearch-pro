# AgResearch Pro

**Agricultural Grants, Research & Funding Management Platform**

---

## Overview

AgResearch Pro is a comprehensive platform for agricultural research organizations, farmers, and consultants to:

- **Discover Grants** - Search federal, state, and private agricultural funding opportunities
- **Manage Applications** - Track deadlines, documents, and submission status
- **Design Research** - Create compliant research protocols and trial designs
- **Track Compliance** - Monitor reporting requirements and milestones
- **Compare Loans** - Analyze FSA and commercial agricultural lending options
- **Generate Reports** - Professional reports for funders and stakeholders

---

## Target Users

| User Type | Use Case |
|-----------|----------|
| **Farmers** | Find grants for conservation, equipment, beginning farmer programs |
| **Research Orgs** | Manage USDA/NIFA research grants, track trials, report outcomes |
| **Ag Consultants** | Apply for grants on behalf of clients, manage portfolios |
| **Co-ops & Ag Retailers** | Access dealer/retailer grant programs |

---

## Key Features

### Grant Discovery
- Federal programs (USDA, NIFA, SARE, NRCS EQIP/CSP)
- State agricultural grants
- Private foundations
- Eligibility matching based on farm profile

### Application Management
- Deadline tracking with reminders
- Document checklist management
- Budget builder with grant-compliant templates
- Collaboration tools for team applications

### Research Management (Powered by AgTools)
- Protocol design templates
- Data collection forms
- Statistical analysis tools (t-tests, ANOVA, LSD)
- Progress reporting
- **7 trial types**: variety, treatment, rate, timing, spacing, fertility, irrigation
- **5 experimental designs**: CRD, RCBD, split-plot, strip-plot, factorial

### Loan Comparison
- FSA loan programs (Operating, Ownership, Emergency)
- Commercial ag lender comparison
- Payment calculators
- Debt service analysis

### Compliance & Reporting
- Milestone tracking
- Financial reporting templates
- Outcome documentation
- Audit preparation

### NRCS Conservation Practices (Powered by AgTools)
- **15 NRCS practice codes** with official documentation requirements
- Practice implementation tracking and verification
- Payment rate estimates per practice
- Carbon benefit calculations (tons CO2e/acre)

### Carbon Credit Integration
- **8 carbon programs**: Nori, Indigo, Bayer, Cargill, Corteva, Nutrien, Gradable, Truterra
- Revenue projections (low/mid/high scenarios)
- Practice-to-program eligibility matching
- Contract term comparisons

### Benchmark Comparisons
- Regional and national performance benchmarks
- Yield, efficiency, sustainability, and economic metrics
- Percentile rankings with improvement recommendations

### Grant Readiness Assessment
- SARE Producer Grant reports
- SBIR/STTR metrics generation
- EQIP application data packages
- CIG compliance reporting
- Multi-program readiness scoring

---

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Templates**: Jinja2

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agresearch-pro.git
cd agresearch-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --reload
```

Open http://localhost:8000 in your browser.

Visit http://localhost:8000/docs for interactive API documentation.

---

## AgTools-Powered API Endpoints

### Field Trials (`/api/v1/trials`)
| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/trials` | List all research trials |
| `POST /api/v1/trials` | Create a new field trial |
| `GET /api/v1/trials/{id}` | Get trial details |
| `GET /api/v1/trials/{id}/treatments` | List trial treatments |
| `POST /api/v1/trials/{id}/treatments` | Add treatment to trial |
| `GET /api/v1/trials/{id}/plots` | List trial plots |
| `POST /api/v1/trials/{id}/plots/generate` | Auto-generate plots |
| `POST /api/v1/trials/measurements` | Record measurement |
| `GET /api/v1/trials/{id}/analysis` | **Statistical analysis** |
| `GET /api/v1/trials/{id}/export` | Export trial data |

### NRCS & Grants (`/api/v1/nrcs`)
| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/nrcs/practices` | List NRCS practices |
| `GET /api/v1/nrcs/practices/{code}` | Get practice details |
| `POST /api/v1/nrcs/implementations` | Record practice implementation |
| `GET /api/v1/nrcs/carbon/programs` | List carbon credit programs |
| `GET /api/v1/nrcs/carbon/calculate` | Calculate carbon credits |
| `GET /api/v1/nrcs/benchmarks` | List benchmark metrics |
| `GET /api/v1/nrcs/benchmarks/compare` | Compare to benchmarks |
| `POST /api/v1/nrcs/reports/sare` | Generate SARE report |
| `POST /api/v1/nrcs/reports/eqip` | Generate EQIP application |
| `POST /api/v1/nrcs/readiness` | **Grant readiness assessment** |

---

## Project Structure

```
agresearch-pro/
├── app/
│   ├── api/              # API route handlers
│   │   ├── grants.py     # Grant discovery API
│   │   ├── applications.py # Application tracking API
│   │   ├── research.py   # Research management API
│   │   ├── loans.py      # Loan comparison API
│   │   ├── trials.py     # Field trials API (AgTools)
│   │   └── nrcs.py       # NRCS & grants API (AgTools)
│   ├── models/           # SQLAlchemy/Pydantic models
│   ├── services/         # Business logic
│   │   └── agtools_integration.py  # AgTools service imports
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── components/   # Reusable UI components
│   │   ├── layouts/      # Page layouts
│   │   └── pages/        # Full page templates
│   └── static/           # CSS, JS, images
├── data/                 # Database files
├── docs/                 # Documentation
├── tests/                # Test suite
├── requirements.txt
└── README.md
```

---

## License

Proprietary - All Rights Reserved

Copyright 2026 New Generation Farms

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited.

---

## Contact

bp3746@icloud.com
