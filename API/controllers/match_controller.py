import logging
from http.client import HTTPException

from fastapi import APIRouter
from fastapi.params import Body, Depends
from fastapi import HTTPException
from API.repos.match_repo import *

from API.database.database import get_db
from API.models.move_model import Move
from API.repos.match_repo import MatchRepository
from API.services.match_service import make_move_service, finish_match_service, update_match_service, \
    get_all_matches_service, create_match_service, delete_all_matches_service
from API.models.match_create import MatchCreate
from API.models.match_out import MatchOut

router = APIRouter()
logger = logging.getLogger(__name__)

# Создание матча
@router.post("/match", response_model=MatchOut)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    try:
        # Вызов функции для создания матча
        new_match = create_match_service(match.player_id, match.player_color, db)

        # Возвращаем созданный матч
        return MatchOut(
            id=new_match.id,
            player_id=new_match.player_id,
            moves=new_match.moves,
            player_color=new_match.player_color,
            status=new_match.status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Получение матча по ID

@router.get("/match/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    try:
        match = MatchRepository.get_match_by_id(match_id, db)

        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Возвращаем данные матча
        return MatchOut(
            id=match.id,
            player_id=match.player_id,
            moves=match.moves or "",  # Заменяем None на пустую строку
            player_color = match.player_color,
            status = match.status
        )

    except HTTPException as e:
        raise e  # Если выброшено HTTPException, просто передаём его дальше

    except Exception as e:
        # Логируем ошибку и возвращаем общий ответ о внутренней ошибке сервера
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/match/{match_id}", status_code=204)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match_repo = MatchRepository(db)
    match_repo.delete_match_by_id(match_id)
    return {"message": "Match deleted successfully"}


# Выполнение хода
@router.post("/match/{match_id}/move")
def make_move(match_id: int, player_move: Move, db: Session = Depends(get_db)):
    result = make_move_service(match_id, player_move.move, db)
    return result
# Завершение матча
@router.post("/match/{match_id}/finish")
def finish_match(match_id: int, db: Session = Depends(get_db)):
    result = finish_match_service(match_id, db)
    return result


@router.put("/match/{match_id}")
def update_match(match_id: int, new_moves: str = Body(...), db: Session = Depends(get_db)):
    return update_match_service(match_id, new_moves, db)
@router.get("/matches", tags=["Matches"])
def get_all_matches(db: Session = Depends(get_db)):
    matches = (
        get_all_matches_service(db))
    return {"matches": matches}

@router.delete("/matches", response_model=dict)
def delete_all_matches(db: Session = Depends(get_db)):
    # Используем сервис для удаления всех матчей
    result = delete_all_matches_service(db)
    return result