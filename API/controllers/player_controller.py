import logging

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from API.database.database import get_db
from API.database.db_models import Player
from API.repos.user_repo import PlayerRepository
from API.models.player_out import PlayerOut
from API.models.player_schema import UserCreate
from API.services.player_service import update_player_service, get_all_players_service, delete_all_players_service

router = APIRouter()
logger = logging.getLogger(__name__)
log_file = "ServerLog.log"
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler()
                    ])
@router.post("/register", response_model=PlayerOut)
def register_player(player: UserCreate, db: Session = Depends(get_db)):
    player_repo = PlayerRepository(db)
    new_player = Player(rating=player.rating)  # Создаем экземпляр Player с rating из UserCreate
    new_player = player_repo.create_player(new_player)  # Сохраняем в БД
    return new_player

@router.get("/player/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player_repo = PlayerRepository(db)
    player = player_repo.get_player_by_id(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.delete("/player/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player_repo = PlayerRepository(db)
    player_repo.delete_player(player_id)
    return {"detail": "Player deleted"}


@router.put("/player/{player_id}")
def update_player(player_id: int, rating: int, db: Session = Depends(get_db)):
    return update_player_service(player_id, rating, db)
@router.get("/players", tags=["Players"])

def get_all_players(db: Session = Depends(get_db)):
    players = get_all_players_service(db)
    return {"players": players}

@router.delete("/players", response_model=dict)
def delete_all_players(db: Session = Depends(get_db)):
    """
    Контроллер для удаления всех игроков из базы данных.
    """
    try:
        result = delete_all_players_service(db)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")