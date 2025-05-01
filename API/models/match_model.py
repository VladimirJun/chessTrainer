# models/match_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
#Entity игры
from API.database.db_models import Base


class Match(Base):
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending")