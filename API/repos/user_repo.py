from typing import Type

from sqlalchemy.orm import Session
from API.database.db_models import Player

class PlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_player(self, player: Player) -> Player:
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def get_player_by_id(self, player_id: int) -> Type[Player] | None:
        return self.db.query(Player).filter(Player.id == player_id).first()

    def update_player(self, player_id: int, rating: int) -> Type[Player] | None:
        player = self.get_player_by_id(player_id)
        if player:
            player.rating = rating
            self.db.commit()
            self.db.refresh(player)
        return player

    def delete_player(self, player_id: int):
        player = self.get_player_by_id(player_id)
        if player:
            self.db.delete(player)
            self.db.commit()
