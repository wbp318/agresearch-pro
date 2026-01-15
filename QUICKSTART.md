# AgResearch Pro - Quick Start Guide

Get up and running in 5 minutes.

---

## Prerequisites

- **Python 3.11+** - Download from https://www.python.org/downloads/
  - During installation, CHECK "Add Python to PATH"
- **Git** - Download from https://git-scm.com/downloads
- **AgTools** - Must be installed alongside AgResearch Pro (same parent directory)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agresearch-pro.git
cd agresearch-pro
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify AgTools Location

AgResearch Pro imports services from AgTools. Ensure your directory structure looks like:

```
Parent Directory/
├── agresearch-pro/    <-- You are here
└── agtools/           <-- AgTools must be here
```

### 5. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

### 6. Open in Browser

- **Web App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Quick Tour

### Web Pages

| URL | Description |
|-----|-------------|
| `/` | Dashboard with stats overview |
| `/grants` | Search and discover grants |
| `/applications` | Track your applications |
| `/research` | Manage research projects |
| `/loans` | Compare loan options |
| `/reports` | Generate reports |
| `/settings` | Configure settings |

### API Endpoints (via /docs)

The interactive API documentation at `/docs` lets you test all endpoints directly.

**Core APIs:**
- `GET /api/v1/grants` - Search grants
- `GET /api/v1/applications` - List applications
- `GET /api/v1/research` - List research projects
- `GET /api/v1/loans` - Compare loans

**AgTools-Powered APIs:**
- `GET /api/v1/trials` - Field trial management
- `GET /api/v1/nrcs/practices` - NRCS conservation practices
- `GET /api/v1/nrcs/carbon/programs` - Carbon credit programs
- `GET /api/v1/nrcs/benchmarks` - Performance benchmarks

---

## Example: Create a Field Trial

### Using the API (via /docs or curl)

**1. Create a Trial:**
```bash
curl -X POST "http://localhost:8000/api/v1/trials" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2026 Corn Hybrid Trial",
    "trial_type": "variety_trial",
    "design": "randomized_complete_block",
    "year": 2026,
    "crop_type": "corn",
    "num_treatments": 5,
    "num_replications": 4,
    "objective": "Compare yield performance of 5 corn hybrids"
  }'
```

**2. Add Treatments:**
```bash
curl -X POST "http://localhost:8000/api/v1/trials/1/treatments" \
  -H "Content-Type: application/json" \
  -d '{
    "trial_id": 1,
    "treatment_number": 1,
    "name": "Pioneer P1197",
    "is_control": true
  }'
```

**3. Generate Plots:**
```bash
curl -X POST "http://localhost:8000/api/v1/trials/1/plots/generate"
```

**4. Record Yield:**
```bash
curl -X POST "http://localhost:8000/api/v1/trials/measurements" \
  -H "Content-Type: application/json" \
  -d '{
    "plot_id": 1,
    "measurement_type": "yield",
    "value": 215.5,
    "unit": "bu/acre",
    "measurement_date": "2026-10-15"
  }'
```

**5. Get Statistical Analysis:**
```bash
curl "http://localhost:8000/api/v1/trials/1/analysis?measurement_type=yield"
```

---

## Example: Calculate Carbon Credits

```bash
# Get carbon credit potential for 500 acres of cover crops
curl "http://localhost:8000/api/v1/nrcs/carbon/calculate?practice_code=340&acres=500&years=5"
```

Response includes revenue projections from all eligible programs:
- Nori, Indigo, Bayer, Cargill, Corteva, Nutrien, Gradable, Truterra

---

## Example: Check Grant Readiness

```bash
curl -X POST "http://localhost:8000/api/v1/nrcs/readiness" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_name": "New Generation Farms",
    "farm_acres": 1500,
    "years_in_operation": 5,
    "current_practices": ["340", "329", "590"],
    "farm_metrics": {
      "corn_yield": 195,
      "cover_crop_adoption": 60,
      "no_till_adoption": 100
    }
  }'
```

Returns readiness scores for SARE, SBIR, CIG, and EQIP programs.

---

## Troubleshooting

### "Module not found" errors

Ensure AgTools is in the correct location:
```
Parent Directory/
├── agresearch-pro/
└── agtools/
```

### Database errors

The database is created automatically in `data/agresearch.db`. If you encounter issues:
```bash
# Delete and recreate
rm data/agresearch.db
python -m uvicorn app.main:app --reload
```

### Port already in use

Use a different port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

---

## Next Steps

1. **Explore the API docs** at http://localhost:8000/docs
2. **Create your first trial** using the trials API
3. **Record NRCS practices** you've implemented
4. **Calculate carbon credits** for your conservation practices
5. **Generate grant reports** for SARE, EQIP, or other programs

---

## Support

**Contact:** bp3746@icloud.com

**Copyright 2026 New Generation Farms. All Rights Reserved.**
