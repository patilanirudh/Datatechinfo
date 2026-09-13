from fastapi import APIRouter, HTTPException

from app.core.config import get_settings

router = APIRouter(prefix="/api", tags=["case-study"])


@router.get("/case-study")
def case_study() -> dict:
    settings = get_settings()
    if not settings.case_study_file.exists():
        raise HTTPException(status_code=404, detail="Case study file not found")
    return {"markdown": settings.case_study_file.read_text(encoding="utf-8")}
