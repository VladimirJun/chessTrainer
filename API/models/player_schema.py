from pydantic import BaseModel

class UserCreate(BaseModel):
    rating: int = 800# По умолчанию рейтинг 800
    username: str
    password: str

    class Config:
        orm_mode = True