from sqlalchemy.orm import Session
from API.database.db_models import Game


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_match_by_id(match_id: int, db: Session):
        return db.query(Game).filter(Game.id == match_id).first()

    def get_all_matches_by_player(self, player_id: int) -> list:
        return self.db.query(Game).filter(Game.player_id == player_id).all()


    def delete_match_by_id(self, match_id: int):
        match = self.db.query(Game).filter(Game.id == match_id).first()
        if match is None:
            raise Exception(f"Match with id {match_id} not found")
        self.db.delete(match)
        self.db.commit()