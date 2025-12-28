from fastapi import APIRouter
from typing import List

from app.api_v1.Students import crud
from app.api_v1.Students import schemas

router = APIRouter()


@router.get("/more-than-3-twos", response_model=List[schemas.StudentTwos])
async def get_students_with_more_than_3_twos():
    """Студенты, у которых оценка 2 встречается больше 3 раз."""
    return await crud.get_students_with_more_than_3_twos()


@router.get("/less-than-5-twos", response_model=List[schemas.StudentTwos])
async def get_students_with_less_than_5_twos():
    """Студенты, у которых оценка 2 встречается меньше 5 раз (и больше 0)."""
    return await crud.get_students_with_less_than_5_twos()