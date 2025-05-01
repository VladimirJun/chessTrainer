from sqlalchemy import Column, Integer, ForeignKey, String, MetaData, DateTime
from sqlalchemy.orm import relationship, declarative_base


metadata = MetaData()
Base = declarative_base(metadata=metadata)
# Сессия для работы с базой данных
class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, default=800)
    username = Column(String(255), index=True)

    games = relationship("Game", back_populates="player")


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    moves = Column(String(255))  # Хранит все ходы в формате PGN
    player = relationship("Player", back_populates="games")
    player_color = Column(String(255))
    first_line_moves = Column(Integer, default=0)
    second_line_moves = Column(Integer, default=0)
    third_line_moves = Column(Integer, default=0)
    bad_moves = Column(Integer, default=0)
    total_moves = Column(Integer, default=0)

    status = Column(String(255), default="in progress")  # Статус игры (например, "finished", "in_progress")
    result = Column(String(255), nullable=True)  # Результат игры ("win", "lose", "draw" и т.д.)
    end_date = Column(DateTime, nullable=True)  # Дата и время окончания игры