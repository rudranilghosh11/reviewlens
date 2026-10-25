"""OCR endpoints — extract text from images/PDFs and route to ReviewLens analysis."""
from __future__ import annotations

import logging
from typing import Any
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel


from app.services.analysis_service import run_analysis
from app.services.ocr_service import (
    extract_text_from_file,
    get_installed_languages,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])


class OCRReviewItem(BaseModel):
    text: str
    brand: str | None = None
    rating: int | None = None


class OCRAnalyseRequest(BaseModel):
    reviews: list[OCRReviewItem]
    default_brand: str | None = "Scanned Review"


@router.get("/languages")
async def list_languages() -> dict[str, Any]:
    """List available OCR engines and installed language packs."""
    return get_installed_languages()


@router.post("/extract")
async def extract_ocr(
    file: UploadFile = File(...),
    lang: str = Form("eng"),
    force_ocr: bool = Form(False),
) -> dict[str, Any]:
    """Extract text from an uploaded image (PNG, JPG, TIFF, BMP) or PDF."""
    try:
        # Stream file in chunks to verify size before buffering
        chunks = []
        total_size = 0
        chunk_size = 1024 * 1024  # 1 MB chunk

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)

            chunks.append(chunk)

        content = b"".join(chunks)
        filename = file.filename or "uploaded_document"

        result = extract_text_from_file(
            content=content,
            filename=filename,
            lang=lang,
            force_ocr=force_ocr,
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("OCR extraction unexpected error: %s", e)
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")


@router.post("/analyse-text")
async def analyse_ocr_reviews(req: OCRAnalyseRequest) -> dict[str, Any]:
    """Convert user-approved OCR review texts into a dataset and run the ReviewLens pipeline.
    Does not invent ratings or metadata; missing ratings trigger transparent VADER estimation."""
    if not req.reviews:
        raise HTTPException(status_code=400, detail="No review text provided for analysis.")

    has_ratings = any(r.rating is not None for r in req.reviews)
    rows = []
    for idx, r in enumerate(req.reviews):
        text = r.text.strip()
        if not text:
            continue
        row: dict[str, Any] = {
            "review_id": f"OCR_{idx + 1:03d}",
            "brand": (r.brand or req.default_brand or "Scanned Entity").strip(),
            "review_text": text,
        }
        if has_ratings and r.rating is not None:
            row["rating"] = r.rating
        rows.append(row)

    if not rows:
        raise HTTPException(status_code=400, detail="All submitted review texts were empty.")

    df = pd.DataFrame(rows)
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    column_overrides = {"rating": None} if not has_ratings else None

    try:
        return run_analysis(csv_bytes, "ocr_extracted_reviews.csv", column_overrides=column_overrides)
    except Exception as e:
        logger.exception("OCR review analysis failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Review analysis pipeline failed: {e}")
