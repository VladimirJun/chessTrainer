from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import chess

from API.services.evaluation_service import EvaluationService
from API.database.database import get_db
from API.schemas.evaluation_schemas import EvaluationResponse, MoveAnalysisRequest

# Создаем роутер
router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post("/analyze_move", response_model=EvaluationResponse)
def analyze_move(request: MoveAnalysisRequest, db: Session = Depends(get_db)):
    """
    Анализирует ход пользователя:
    - Вычисляет оценку **до** и **после** хода
    - Определяет ухудшения параметров
    - Генерирует объяснение ошибок
    """

    try:
        # Инициализируем сервис
        evaluation_service = EvaluationService()

        # Преобразуем строку хода в объект `chess.Move`
        move = chess.Move.from_uci(request.user_move)

        # Запускаем анализ
        analysis_result = evaluation_service.analyze_move(request.fen_before, move)

        return EvaluationResponse(
            evaluation_before=analysis_result["evaluation_before"],
            evaluation_after=analysis_result["evaluation_after"],
            worsened_params=analysis_result["worsened_params"],
            feedback_messages=analysis_result["feedback_messages"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
