from sqlalchemy.orm import Session
from .db_models import Player
from ChessAI.API.models.player_schema import UserCreate

# Создание пользователя
def create_player(db: Session, user: UserCreate):
    db_player = Player()
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# Получение пользователя по id
def get_player(db: Session, player_id: int):
    return db.query(Player).filter(Player.id == player_id).first()