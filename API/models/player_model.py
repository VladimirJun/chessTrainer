from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from  API.database.db_models import Base
class Player(Base):
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, default=800)
    matches = relationship("games", back_populates="players")
