from fastapi import APIRouter
from app.api_v1.Students.views import router as student_router
from app.api_v1.Grades.views import router as grades_router

api_router = APIRouter()

api_router.include_router(student_router, prefix="/students", tags=["Students"])
api_router.include_router(grades_router, tags=["Grades"])


@api_router.get("/healthcheck")
def healthcheck():
    """Simple healthcheck endpoint."""
    return {"status": "ok"}