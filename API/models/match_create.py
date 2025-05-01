from pydantic import BaseModel
class MatchCreate(BaseModel):
    id: int
    player_id:int
    moves:str
    player_color:str
