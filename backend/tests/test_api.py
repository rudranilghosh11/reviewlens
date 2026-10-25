from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_missing_review_text_returns_400():
    response = client.post(
        "/api/analyse",
        files={"file": ("no-review.csv", b"product,rating\nHeadphones,5\n", "text/csv")},
    )
    assert response.status_code == 400
    assert "review" in response.json()["detail"].lower()

def test_brief_docx_requires_analysis():
    import backend.app.api.routes as routes
    previous = routes._last_result
    try:
        routes._last_result = None
        response = client.get("/api/brief.docx")
        assert response.status_code == 404
    finally:
        routes._last_result = previous
