"""Brief generation endpoint."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from app.services.analysis_service import generate_brief

router = APIRouter(tags=["brief"])


@router.get("/brief/{analysis_id}", response_class=PlainTextResponse)
async def brief(analysis_id: str, brand: str = Query("All brands")):
    """Generate and return the PM brief as markdown text."""
    try:
        md = generate_brief(analysis_id, brand)
        return PlainTextResponse(content=md, media_type="text/markdown")
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
