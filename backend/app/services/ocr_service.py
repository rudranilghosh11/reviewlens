"""OCR & Document Text Extraction Service.

Extracts text from images (PNG, JPEG, TIFF, BMP) and multi-page PDFs
using Tesseract (pytesseract) with native Windows OCR (winocr) fallback.
Extracts direct selectable text from PDFs when available and applies OCR
to scanned pages incrementally to minimize memory consumption.
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

from app.core.config import MAX_UPLOAD_BYTES, MAX_UPLOAD_SIZE_MB, TESSERACT_CMD

# ── Magic Byte Verification ──────────────────────────────────────────────────
MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpeg": [b"\xff\xd8\xff"],
    "tiff": [b"II*\x00", b"MM\x00*"],
    "bmp": [b"BM"],
    "pdf": [b"%PDF-"],
}


def detect_file_type(header: bytes) -> str | None:
    """Validate binary file signature rather than trusting filename or browser MIME."""
    for file_type, signatures in MAGIC_SIGNATURES.items():
        for sig in signatures:
            if header.startswith(sig):
                return file_type
    return None


# ── OCR Engine Discovery ─────────────────────────────────────────────────────
_tesseract_cmd: str | None = None
_tesseract_checked: bool = False


def get_tesseract_path() -> str | None:
    global _tesseract_cmd, _tesseract_checked
    if _tesseract_checked:
        return _tesseract_cmd

    candidates = [
        TESSERACT_CMD,
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]

    for cand in candidates:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            _tesseract_cmd = cand
            break

    _tesseract_checked = True
    return _tesseract_cmd


def get_installed_languages() -> dict[str, Any]:
    """Returns list of actually installed OCR languages and active engine."""
    tess_path = get_tesseract_path()
    if tess_path:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tess_path
            langs = pytesseract.get_languages(config="")
            valid_langs = [l for l in langs if l != "osd"]
            if "eng" in valid_langs:
                valid_langs.remove("eng")
                valid_langs.insert(0, "eng")
            return {
                "engine": f"Tesseract OCR ({tess_path})",
                "default_language": "eng",
                "languages": valid_langs or ["eng"],
                "has_tesseract": True,
            }
        except Exception:
            pass

    # Windows Native OCR fallback
    try:
        import winocr
        langs = winocr.get_available_languages()
        default_lang = "en-US" if "en-US" in langs else (langs[0] if langs else "en-US")
        if "en-US" in langs:
            langs.remove("en-US")
            langs.insert(0, "en-US")
        return {
            "engine": "Windows Native OCR (Windows.Media.Ocr)",
            "default_language": default_lang,
            "languages": langs or ["en-US"],
            "has_tesseract": False,
        }
    except Exception:
        return {
            "engine": "Basic Text Extraction (PDF Selectable Text Only)",
            "default_language": "en",
            "languages": ["en"],
            "has_tesseract": False,
        }


def _ocr_pil_image(img: Image.Image, lang: str = "eng") -> str:
    """Run OCR on a PIL Image using available engine."""
    tess_path = get_tesseract_path()
    if tess_path:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tess_path
            return pytesseract.image_to_string(img, lang=lang).strip()
        except Exception:
            pass

    # Fallback to winocr (execute in thread to avoid event loop conflicts in async endpoints)
    try:
        import concurrent.futures
        import winocr
        win_lang = "en-US" if lang.startswith("eng") or lang == "en" else lang
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            res = executor.submit(winocr.recognize_pil_sync, img, win_lang).result()
        if isinstance(res, dict):
            return res.get("text", "").strip()
        return getattr(res, "text", "").strip()
    except Exception as e:
        raise RuntimeError(f"OCR engine failure: {e}") from e


# ── PDF Processing ───────────────────────────────────────────────────────────
def _extract_from_pdf(content: bytes, lang: str = "eng", force_ocr: bool = False) -> dict[str, Any]:
    """Incrementally extracts text from PDF pages, preferring selectable text
    and falling back to page OCR for scanned pages."""
    import pypdf
    import pypdfium2 as pdfium

    pdf_stream = io.BytesIO(content)
    reader = pypdf.PdfReader(pdf_stream)
    total_pages = len(reader.pages)

    if total_pages == 0:
        raise ValueError("The uploaded PDF has 0 pages.")

    pages_result: list[dict[str, Any]] = []
    warnings: list[str] = []
    full_text_parts: list[str] = []

    # Open with pdfium only if needed for scanned pages
    pdfium_doc = None

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        page_text = ""
        method = "direct"
        page_warning = None

        if not force_ocr:
            try:
                extracted = page.extract_text() or ""
                # If we got meaningful selectable text (>= 30 non-whitespace chars)
                if len(re.sub(r"\s+", "", extracted)) >= 30:
                    page_text = extracted.strip()
                    method = "direct"
            except Exception as e:
                page_warning = f"Direct text extraction failed on page {page_num}: {e}"

        # If selectable text was empty or sparse, perform OCR on this page
        if not page_text:
            try:
                if pdfium_doc is None:
                    pdfium_doc = pdfium.PdfDocument(content)
                pdf_page = pdfium_doc[i]
                # Render at 1.5x scale (~108 DPI) for balance of speed and clarity
                pil_img = pdf_page.render(scale=1.5).to_pil()
                page_text = _ocr_pil_image(pil_img, lang=lang)
                method = "ocr"
                del pil_img
            except Exception as e:
                page_warning = f"Page {page_num} OCR failed: {e}"
                warnings.append(page_warning)

        char_count = len(page_text)
        if page_text:
            full_text_parts.append(f"--- [Page {page_num}] ---\n{page_text}")

        pages_result.append({
            "page_number": page_num,
            "method": method,
            "text": page_text,
            "char_count": char_count,
            "warning": page_warning,
        })

    if pdfium_doc:
        pdfium_doc.close()

    full_text = "\n\n".join(full_text_parts)
    return {
        "total_pages": total_pages,
        "pages": pages_result,
        "full_text": full_text,
        "warnings": warnings,
    }


# ── Image Processing ─────────────────────────────────────────────────────────
def _extract_from_image(content: bytes, lang: str = "eng") -> dict[str, Any]:
    """Extracts text from a single image."""
    try:
        img = Image.open(io.BytesIO(content))
        img.load()
    except Exception as e:
        raise ValueError(f"Corrupted or unreadable image file: {e}") from e

    text = _ocr_pil_image(img, lang=lang)
    return {
        "total_pages": 1,
        "pages": [
            {
                "page_number": 1,
                "method": "ocr",
                "text": text,
                "char_count": len(text),
                "warning": None,
            }
        ],
        "full_text": text,
        "warnings": [],
    }


# ── Review Segmentation Strategy ─────────────────────────────────────────────
def segment_extracted_reviews(text: str) -> list[dict[str, Any]]:
    """Segment extracted text into discrete review candidates only when reliable
    structure is identified; otherwise return as single candidate."""
    cleaned = text.strip()
    if not cleaned:
        return []

    # Check for explicit review separators, e.g. "Review 1:", "Review #1", "---", "[Page N]"
    delimiters = [
        r"(?i)(?:^|\n)(?:review\s*#?\s*\d+[:\-\.]|feedback\s*#?\s*\d+[:\-\.])",
        r"(?i)(?:^|\n)(?:[-=_]{3,}|[*]{3,})",
        r"(?i)(?:^|\n)--- \[Page \d+\] ---",
    ]

    candidates: list[str] = []
    for pat in delimiters:
        parts = re.split(pat, cleaned)
        valid = [p.strip() for p in parts if len(p.strip()) > 15]
        if len(valid) > 1:
            candidates = valid
            break

    # If no delimiter pattern, test paragraph blocks separated by double newlines
    if not candidates:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if len(p.strip()) > 25]
        if 1 < len(paragraphs) <= 30:
            candidates = paragraphs
        else:
            candidates = [cleaned]

    return [{"id": idx + 1, "text": c} for idx, c in enumerate(candidates)]


# ── Public Entrypoint ────────────────────────────────────────────────────────
def extract_text_from_file(
    content: bytes,
    filename: str,
    lang: str = "eng",
    force_ocr: bool = False,
) -> dict[str, Any]:
    """Full extraction pipeline validating size, magic bytes, and processing
    PDF or image."""
    file_size = len(content)

    # 1. Size Validation
    if file_size > MAX_UPLOAD_BYTES:
        actual_mb = file_size / (1024 * 1024)
        raise ValueError(
            f"File too large ({actual_mb:.1f} MB / {file_size:,} bytes). "
            f"Maximum permitted size is {MAX_UPLOAD_SIZE_MB} MB ({MAX_UPLOAD_BYTES:,} bytes)."
        )

    if file_size == 0:
        raise ValueError("Uploaded file is empty (0 bytes).")

    # 2. Content Signature Validation
    header = content[:32]
    detected_type = detect_file_type(header)

    allowed_exts = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".pdf"}
    ext = Path(filename).suffix.lower()

    if not detected_type:
        raise ValueError(
            f"Unsupported or corrupted file content. File '{filename}' does not match "
            "supported binary formats: PNG, JPG/JPEG, TIFF, BMP, or PDF."
        )

    # 3. Process according to detected format
    engine_info = get_installed_languages()

    if detected_type == "pdf":
        result = _extract_from_pdf(content, lang=lang, force_ocr=force_ocr)
    else:
        result = _extract_from_image(content, lang=lang)

    segmented = segment_extracted_reviews(result["full_text"])

    return {
        "filename": filename,
        "file_size": file_size,
        "detected_type": detected_type,
        "engine": engine_info["engine"],
        "language": lang,
        "total_pages": result["total_pages"],
        "pages": result["pages"],
        "full_text": result["full_text"],
        "detected_reviews": segmented,
        "warnings": result["warnings"],
    }
