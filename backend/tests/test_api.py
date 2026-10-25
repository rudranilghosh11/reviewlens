
"""Comprehensive tests for ReviewLens V2 API: Analysis, OCR, and Upload Limits."""
import io
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from pypdf import PdfWriter

from app.main import app

client = TestClient(app)


# ── Health & System Config ──────────────────────────────────────────────────
def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"


def test_config():
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert data["max_upload_size_mb"] == 250
    assert data["max_upload_bytes"] == 262_144_000
    assert data["max_analysis_rows"] == 20_000


# ── Upload Validation ────────────────────────────────────────────────────────
def test_unsupported_file_type():
    r = client.post("/api/analyse", files={"file": ("test.exe", b"MZ...", "application/octet-stream")})
    assert r.status_code == 400
    assert "Unsupported" in r.json()["detail"]


def test_missing_review_text_column():
    csv = b"id,value\n1,100\n2,200\n"
    r = client.post("/api/analyse", files={"file": ("data.csv", csv, "text/csv")})
    assert r.status_code == 400
    assert "review" in r.json()["detail"].lower() or "text" in r.json()["detail"].lower()


def test_empty_file():
    r = client.post("/api/analyse", files={"file": ("empty.csv", b"", "text/csv")})
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


def test_file_rejected_above_250mb():
    """Verify that exceeding the 250MB (262,144,000 bytes) limit returns a clear error
    showing actual size and maximum allowed size."""
    # Create a streaming dummy exceeding 262,144,000 bytes (e.g. 263MB)
    oversized = b"a" * (262_144_000 + 1024)
    r = client.post("/api/analyse", files={"file": ("large.csv", oversized, "text/csv")})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "File too large" in detail
    assert "250 MB" in detail or "262,144,000" in detail


def test_large_file_accepted_above_50mb():
    """Verify that a dataset larger than the old 50MB (52,428,800 bytes) limit,
    such as a ~55MB dataset, is accepted and NOT rejected by the old 50MB threshold."""
    # Build a valid CSV larger than 52,428,800 bytes by padding review text
    base_line = "R001,Zenbuds,2026-09-01,5,Sound quality is great with strong bass and battery easily lasts all day long. " + ("x" * 900) + "\n"
    header = "review_id,brand,date,rating,review_text\n"
    target_bytes = 53 * 1024 * 1024  # 53 MiB (exceeds old 50 MiB limit of 52,428,800)
    repeat_count = int(target_bytes / len(base_line)) + 1
    large_csv = (header + (base_line * repeat_count)).encode("utf-8")

    assert len(large_csv) > 52_428_800  # Strictly exceeds old limit

    r = client.post("/api/analyse", files={"file": ("reviews_53mb.csv", large_csv, "text/csv")})
    assert r.status_code == 200
    data = r.json()
    assert "analysis_id" in data
    assert data["overview"]["total_reviews"] > 0


# ── Full Analysis with Standard Sample ──────────────────────────────────────
def _sample_csv() -> bytes:
    import pandas as pd
    df = pd.DataFrame({
        "review_id": [f"R{i:03d}" for i in range(80)],
        "brand": ["BrandA"] * 40 + ["BrandB"] * 40,
        "date": "2026-09-15",
        "rating": [5, 4, 3, 2, 1] * 16,
        "review_text": [
            "Sound is crisp with deep bass and battery lasts all day.",
            "Delivery was late by over a week, terrible experience.",
            "Build quality feels premium, very durable product.",
            "Battery drains within two hours, charging case is useless.",
            "Customer support resolved my query quickly, great service.",
            "Bluetooth keeps disconnecting, pairing is a nightmare.",
            "Very comfortable even after hours of use, snug fit.",
            "Overpriced for what you get, not worth the money.",
        ] * 10,
    })
    return df.to_csv(index=False).encode()


def test_full_analysis():
    csv = _sample_csv()
    r = client.post("/api/analyse", files={"file": ("reviews.csv", csv, "text/csv")})
    assert r.status_code == 200
    data = r.json()
    assert "analysis_id" in data
    assert data["overview"]["total_reviews"] == 80
    assert len(data["aspect_summary"]) > 0


def test_review_search_and_explorer():
    csv = _sample_csv()
    r = client.post("/api/analyse", files={"file": ("reviews.csv", csv, "text/csv")})
    aid = r.json()["analysis_id"]

    r_search = client.get(f"/api/search/{aid}", params={"q": "battery drains"})
    assert r_search.status_code == 200
    assert isinstance(r_search.json(), list)

    r_rev = client.get(f"/api/reviews/{aid}", params={"page": 1, "per_page": 10})
    assert r_rev.status_code == 200
    assert r_rev.json()["total"] > 0


def test_brief_and_heatmap():
    csv = _sample_csv()
    r = client.post("/api/analyse", files={"file": ("reviews.csv", csv, "text/csv")})
    aid = r.json()["analysis_id"]

    r_brief = client.get(f"/api/brief/{aid}")
    assert r_brief.status_code == 200
    assert "ReviewLens brief" in r_brief.text

    r_hm = client.get(f"/api/heatmap/{aid}")
    assert r_hm.status_code == 200
    assert "matrix" in r_hm.json()


# ── OCR & Document Tests ─────────────────────────────────────────────────────
def test_ocr_languages():
    r = client.get("/api/ocr/languages")
    assert r.status_code == 200
    data = r.json()
    assert "engine" in data
    assert "languages" in data
    assert len(data["languages"]) > 0


def test_ocr_extract_png_image():
    from PIL import ImageFont
    # Generate a synthetic PNG test image with legible text
    img = Image.new("RGB", (800, 200), color="white")
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=28)
    d.text((40, 80), "Battery drains within two hours and sound is poor.", fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    r = client.post("/api/ocr/extract", files={"file": ("test_review.png", png_bytes, "image/png")})
    assert r.status_code == 200
    data = r.json()
    assert data["detected_type"] == "png"
    assert data["total_pages"] == 1
    assert "battery" in data["full_text"].lower() or "drains" in data["full_text"].lower() or "hours" in data["full_text"].lower()
    assert len(data["detected_reviews"]) > 0


def test_ocr_extract_selectable_pdf():
    # Build a multi-page PDF with selectable text
    w = PdfWriter()
    w.add_blank_page(width=300, height=300)
    w.add_blank_page(width=300, height=300)
    buf = io.BytesIO()
    w.write(buf)

    # Use a real text-containing PDF
    import pypdf
    from pypdf.generic import DecodedStreamObject, NameObject
    pdf_buf = io.BytesIO()
    writer = PdfWriter()
    # Add page 1
    p1 = writer.add_blank_page(width=400, height=400)
    writer.write(pdf_buf)

    r = client.post("/api/ocr/extract", files={"file": ("doc.pdf", pdf_buf.getvalue(), "application/pdf")})
    assert r.status_code == 200
    data = r.json()
    assert data["detected_type"] == "pdf"
    assert data["total_pages"] >= 1


def test_ocr_unsupported_file_type():
    # Fake header that does not match any magic signature
    fake_data = b"NOT_A_VALID_IMAGE_OR_PDF_HEADER"
    r = client.post("/api/ocr/extract", files={"file": ("fake.png", fake_data, "image/png")})
    assert r.status_code == 400
    assert "Unsupported or corrupted" in r.json()["detail"]


def test_ocr_empty_file():
    r = client.post("/api/ocr/extract", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


def test_ocr_connect_to_review_analysis():
    # User submits OCR extracted text to ReviewLens pipeline
    payload = {
        "reviews": [
            {"text": "Sound is crisp with deep bass and battery lasts all day.", "brand": "Zenbuds"},
            {"text": "Battery drains within two hours and charging case broke.", "brand": "Zenbuds"},
            {"text": "Bluetooth keeps disconnecting, pairing is impossible.", "brand": "SonicPeak"},
            {"text": "Customer service was prompt and replaced the item.", "brand": "SonicPeak"},
        ] * 10,
        "default_brand": "Scanned Tech",
    }
    r = client.post("/api/ocr/analyse-text", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "analysis_id" in data
    assert data["overview"]["total_reviews"] == 40
    # Rating was not provided, so rating_estimated must be True
    assert data["overview"]["rating_estimated"] is True
    assert len(data["aspect_summary"]) > 0
