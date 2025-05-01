from pydantic import BaseModel
from typing import Dict, List

from pydantic import ConfigDict

from API.services.evaluation_service import Evaluation

class MoveAnalysisRequest(BaseModel):
    """Запрос для анализа хода"""
    fen_before: str
    user_move: str

class EvaluationResponse(BaseModel):
    """Ответ API с разбором ухудшений"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    evaluation_before: Evaluation
    evaluation_after: Evaluation
    worsened_params: Dict[str, float]
    feedback_messages: List[str]