from pydantic import BaseModel
from typing import List


from typing import Optional

class ValidationErrorItem(BaseModel):
    row: int
    detail: str



class UploadResult(BaseModel):
    status: str
    records_loaded: int
    students: int
    errors: Optional[List[ValidationErrorItem]] = None


