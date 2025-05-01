import logging

from sqlalchemy.orm import Session

from API.database.db_models import Player
from fastapi import HTTPException

players = {}
logger = logging.getLogger(__name__)
class PlayerService:


    def create_player_service(player: Player):
        players[player.id] = {
            'rating': player.rating,
            'games': player.games
        }
        return player.id


    def get_player_service(player_id: int):
        if player_id not in players:
            logger.error('Player not found')
            raise HTTPException(status_code=404, detail="Player not found")
        return players[player_id]

def update_player_service(player_id: int, rating: int, db: Session):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player.rating = rating
    db.commit()
    return player


def delete_all_players_service(db: Session):
    # Удаляем всех игроков из базы
    """Удаление всей базы игроков """
    try:
        players = db.query(Player).all()
        if not players:
            raise HTTPException(status_code=404, detail="No players found")

        # Удаление всех игроков
        for player in players:
            db.delete(player)

        db.commit()
        return {"message": "All players have been deleted"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def get_all_players_service(db: Session):
    """
    Получить список всех игроков из базы данных.
    """
    players = db.query(Player).all()
    return players