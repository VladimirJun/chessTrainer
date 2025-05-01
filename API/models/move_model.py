from pydantic import BaseModel


class Move(BaseModel):
    move: str