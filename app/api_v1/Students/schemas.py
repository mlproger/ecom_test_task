from pydantic import BaseModel


class StudentTwos(BaseModel):
    full_name: str
    count_twos: int
