"""Analysis endpoints — upload, review explorer, search, competitor heatmap, configuration."""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.core.config import MAX_ANALYSIS_ROWS, MAX_UPLOAD_BYTES, MAX_UPLOAD_SIZE_MB
from app.services.analysis_service import (
    get_competitor_heatmap,
    get_reviews,
    run_analysis,
    search_session,
)

router = APIRouter(tags=["analysis"])


@router.get("/config")
async def get_system_config():
    """Return backend upload limits and analysis parameters for client-side validation."""
    return {
        "max_upload_size_mb": MAX_UPLOAD_SIZE_MB,
        "max_upload_bytes": MAX_UPLOAD_BYTES,
        "max_analysis_rows": MAX_ANALYSIS_ROWS,
    }


@router.post("/analyse")
async def analyse(file: UploadFile = File(...)):
    """Upload a review dataset and run the full ReviewLens analysis pipeline."""
    # Chunked read to prevent buffering oversized files in RAM
    chunks = []
    total_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_UPLOAD_BYTES:
            actual_mb = total_size / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File too large ({actual_mb:.1f} MB / {total_size:,} bytes). "
                    f"Maximum permitted size is {MAX_UPLOAD_SIZE_MB} MB ({MAX_UPLOAD_BYTES:,} bytes)."
                ),
            )
        chunks.append(chunk)

    if total_size == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty (0 bytes).")

    content = b"".join(chunks)

    # Extension guard
    name = file.filename or "upload.csv"
    allowed = (
        ".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls",
        ".json", ".jsonl", ".ndjson", ".parquet", ".gz",
    )
    if not any(name.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {name}")

    try:
        result = run_analysis(content, name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {type(e).__name__}: {e}")

    return result


@router.get("/reviews/{analysis_id}")
async def reviews(
    analysis_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    brand: str | None = None,
    sentiment: str | None = None,
):
    """Paginated review explorer for a completed analysis."""
    try:
        return get_reviews(analysis_id, page, per_page, brand, sentiment)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/search/{analysis_id}")
async def search(
    analysis_id: str,
    q: str = Query(..., min_length=1),
    k: int = Query(10, ge=1, le=50),
):
    """Search reviews by natural-language query using TF-IDF retrieval."""
    try:
        return search_session(analysis_id, q, k)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/heatmap/{analysis_id}")
async def heatmap(analysis_id: str):
    """Brand × aspect net sentiment matrix for competitor comparison."""
    try:
        return get_competitor_heatmap(analysis_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
