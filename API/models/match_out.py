from pydantic import BaseModel
class MatchOut(BaseModel):
    id: int
    player_id: int
    moves: str
    player_color: str
    status: str

    class Config:
        orm_mode = True
