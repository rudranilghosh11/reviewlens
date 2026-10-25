# ReviewLens V2 — Customer Voice Intelligence Platform

A rebuild of Review Lens replacing the Streamlit interface with a high-performance **FastAPI backend** and **React + Vite frontend** executing the **Lamborghini visual design specification** (`DESIGN-lamborghini.md`).

---

## Architecture Overview

```
reviewlens/ (and reviewlens-v2/)
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py        # GET /api/health
│   │   │   ├── analyse.py       # POST /api/analyse, GET /api/reviews, GET /api/search, GET /api/heatmap
│   │   │   └── brief.py         # GET /api/brief
│   │   ├── core/
│   │   │   └── config.py        # Upload size guards & analysis row limits
│   │   ├── schemas/
│   │   │   └── analysis.py      # Typed Pydantic models for responses & telemetry
│   │   ├── services/
│   │   │   └── analysis_service.py # Non-HTTP orchestrator calling real src/ logic
│   │   └── main.py              # FastAPI app with CORS middleware
│   ├── tests/
│   │   └── test_api.py          # 10 automated test cases (pytest)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # Typed API client
│   │   ├── components/
│   │   │   ├── Navbar.tsx       # Hexagonal branding & engine status telemetry
│   │   │   ├── UploadHero.tsx   # Drag & drop upload, sample dataset loader, progress pipeline
│   │   │   ├── OverviewCards.tsx # Key KPI cards & executive telemetry briefing
│   │   │   ├── IssuesTable.tsx  # Priority Fix-First matrix with verbatim quote drawers
│   │   │   ├── AspectsCard.tsx  # Pos/Neu/Neg aspect sentiment breakdown
│   │   │   ├── EmergingAndRisks.tsx # Spikes, risk triggers, regression key drivers & signal words
│   │   │   ├── HeatmapView.tsx  # Brand × aspect competitor net sentiment matrix
│   │   │   ├── SearchExplorer.tsx # TF-IDF evidence retrieval & full-text search
│   │   │   └── BriefView.tsx    # Synthesized executive PM brief with Markdown export
│   │   ├── types/analysis.ts    # TypeScript definitions matching Pydantic schemas
│   │   ├── index.css            # Lamborghini design tokens (True Black, Gold, 0px radius)
│   │   └── App.tsx
│   ├── public/reviews.csv       # 3,200 sample earbud reviews for 1-click evaluation
│   └── package.json
├── src/                         # Original analysis modules preserved
│   ├── ingest.py
│   ├── pipeline.py
│   ├── discovery.py
│   ├── insights.py              # Fixed min_df boundary condition for small sets
│   ├── search.py
│   └── brief.py
└── start.bat                    # One-click Windows startup script
```

---

## Design System Execution

- **True Black Dominance**: `#000000` canvas with `#101010`–`#222222` elevated telemetry surfaces.
- **Lamborghini Gold Accent**: `#FFC000` for primary actions, CTA buttons, and high-priority metrics; hover `#917300`.
- **Zero Border-Radius**: `border-radius: 0px` across all cards, buttons, badges, tables, and inputs for razor-sharp aerodynamic aesthetics.
- **Typography**: Display headings in `Chakra Petch` (all-caps with wide tracking); body text in clean high-contrast `Inter`.
- **Informational Accents**: Cyan pulse (`#29ABE2`) for secondary metrics and search highlights; signal red (`#FF334B`) for critical priority issues.

---

## Verification & Testing

### 1. Automated Backend Tests
Run the 10 automated test cases:
```powershell
$env:PYTHONPATH = "$PWD;$PWD\backend"
python -m pytest backend/tests -v
```
All 10 tests pass:
- `test_health`
- `test_unsupported_file_type`
- `test_missing_review_text_column`
- `test_empty_file`
- `test_full_analysis`
- `test_review_search`
- `test_review_explorer`
- `test_brief_generation`
- `test_session_not_found`
- `test_heatmap`

### 2. Frontend Build
```powershell
cd frontend
npm run build
```
Builds cleanly with zero TypeScript errors or linter warnings.

---

## Running Locally on Windows

### Quick Launch
Double-click `start.bat` in the root folder, or run:
```cmd
start.bat
```

### Manual Launch

**Terminal 1 — Backend:**
```powershell
$env:PYTHONPATH = "$PWD;$PWD\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

Open your browser at **http://127.0.0.1:5173**.
