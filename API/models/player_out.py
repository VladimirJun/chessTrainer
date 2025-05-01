from pydantic import BaseModel

class PlayerOut(BaseModel):
    id: int
    # username:str
    rating: int


    class Config:
        orm_mode = True