from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.api_v1.Grades import service, schemas

router = APIRouter()


@router.post("/upload-grades", response_model=schemas.UploadResult, status_code=status.HTTP_200_OK)
async def upload_grades(file: UploadFile = File(...)):
    """Загрузка данных из CSV файла."""
    if not (file.filename and file.filename.lower().endswith(".csv")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .csv files are allowed")

    try:
        records_loaded, students_count, errors = await service.load_grades(file)


        resp = {"status": "ok", "records_loaded": records_loaded, "students": students_count}
        if errors:
            resp["errors"] = [e.model_dump() for e in errors]
        return resp
    finally:
        await file.close()