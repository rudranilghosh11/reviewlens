# Review Lens

Review Lens turns product reviews into evidence-backed priorities for product teams. The application uses a React + Vite frontend and FastAPI backend. The existing `src/` analysis modules are retained.

## Features

- CSV, TSV, TXT, Excel, JSON/JSONL and optional Parquet ingestion using the existing ingestion module.
- Automatic column detection and review cleaning.
- Aspect-level sentiment, priority issues, emerging issue alerts, risk signals, key drivers, weekly trends, and executive summary when the underlying modules can calculate them.
- Search over analysed reviews, an on-screen product-manager brief, and Word (.docx) brief download.
- No fixed application-level upload size cap. Practical processing is still bounded by available RAM, disk, and time.

## Windows setup

Install Python 3.11 or newer and Node.js LTS. From this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. API docs: `http://127.0.0.1:8000/docs`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal and activate again.

## Tests

```powershell
python -m pytest -q backend/tests
```

Synthetic data and synthetic labels are for pipeline sanity checks, not evidence of real-world model accuracy. Evaluate on human-labelled real reviews before reporting model quality.

## Product-manager brief

After a successful analysis, the Executive Overview displays the generated product-manager brief on screen. Use **DOWNLOAD BRIEF (.DOCX)** to export the same analysis-derived brief as a Microsoft Word document. The export includes the brief's title, headings, findings, evidence quotes, and suggested actions. The download endpoint requires an analysis to have completed in the current backend session.

## Project continuity and scope

- Keep the original analysis engine in `src/`; the API orchestrates these existing functions rather than reimplementing them.
- The frontend is React + Vite and the backend is FastAPI. Streamlit is not part of this project.
- OCR has been removed as requested. File upload is for structured review datasets; image/scanned-document OCR is not included.
- Uploads have no fixed application-level byte cap. Real limits still depend on available RAM, disk space, and processing time.
- The app displays the latest generated brief and exports it to `.docx` using `python-docx`.
