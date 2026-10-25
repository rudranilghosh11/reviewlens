from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from src.ingest import read_upload, standardize, guess_columns
from src.pipeline import analyse as run_analysis

router = APIRouter()

@router.post("/analyse")
async def analyse(file: UploadFile = File(...)):
    """Accept a CSV/Excel/JSON/etc. review file, run the full Review Lens pipeline, and return a tiny summary.
    The full result format will be expanded later; for now we return counts to prove end‑to‑end flow.
    """
    try:
        # read raw bytes
        content = await file.read()
        df, enc = read_upload(file.filename, len(content), content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")

    # Auto‑map columns using the same heuristic Streamlit UI uses
    guess = guess_columns(df)
    # Build a simple mapping dict – if a required column is missing we error
    required = ["review_text"]
    for col in required:
        if guess.get(col) is None:
            raise HTTPException(status_code=400, detail=f"Missing required column for {col}")
    # Use the guessed mapping for standardize; keep other columns as‑is
    mapping_items = [(k, v) for k, v in guess.items() if v]
    try:
        # For now we keep brand_first_word False and cap at 20000 rows (same as UI default)
        out = standardize(df, dict(mapping_items), max_rows=20000, brand_first_word=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data standardisation failed: {e}")

    try:
        reviews, asp, discovered = run_analysis(out, n_topics=0, use_ratings=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {e}")

    # Return a minimal payload – we will extend later
    return {
        "total_reviews": int(len(reviews)),
        "usable_reviews": int(len(reviews[~reviews.flagged])),
        "aspects": len(asp),
        "discovered": discovered,
    }
