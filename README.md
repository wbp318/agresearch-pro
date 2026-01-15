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

### Research Management
- Protocol design templates
- Data collection forms
- Statistical analysis tools
- Progress reporting

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

---

## Project Structure

```
agresearch-pro/
├── app/
│   ├── api/              # API route handlers
│   ├── models/           # SQLAlchemy/Pydantic models
│   ├── services/         # Business logic
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── components/   # Reusable UI components
│   │   ├── layouts/      # Page layouts
│   │   └── pages/        # Full page templates
│   └── static/           # CSS, JS, images
├── data/                 # Grant database, seed data
├── docs/                 # Documentation
├── tests/                # Test suite
├── requirements.txt
└── README.md
```

---

## License

Proprietary - All Rights Reserved

Copyright 2026 [Your Company Name]

---

## Contact

[Your contact information]
