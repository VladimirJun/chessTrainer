from datetime import datetime

import chess.pgn
from fastapi import HTTPException
from sqlalchemy.orm import Session

from API.database.db_models import Player, Game
from API.assistant.assistant_messages import generate_feedback, analyze_deltas
from chess_trainer.game_analyze.chess_utils import get_best_move, update_engine_level, classify_move, \
    append_single_move_to_pgn, restore_board_from_pgn
from chess_trainer.model.game import logger, predict_user_rating
from API.services.evaluation_service import EvaluationService
# Функция для создания нового матча
def create_match_service(player_id: int, player_color: str, db: Session):
    # Проверяем корректность значения player_color
    if player_color not in ["white", "black"]:
        raise ValueError("Invalid player color. Choose 'white' or 'black'.")
    if player_color=='black':
        board = chess.Board()
        engine_move = get_best_move(board)
    # Создаем новый матч
        new_game = Game(
            player_id=player_id,
            moves=append_single_move_to_pgn("",engine_move,board) ,
            player_color=player_color,
            status = "in progress"
        )
    else:
        new_game = Game(
            player_id=player_id,
            moves="",
            player_color=player_color,
            status="in progress"
        )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game


def make_move_service(game_id: int, user_move: str, db: Session):
    #Получаем игру из БД
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise ValueError(f"Game with ID {game_id} not found")

    #Восстанавливаем доску
    board = restore_board_from_pgn(game.moves if game.moves else "")

    #Проверяем корректность хода
    move = chess.Move.from_uci(user_move)
    if move not in board.legal_moves:
        raise ValueError("Illegal move")

        #Получаем оценку позиции до хода
    evaluation_service = EvaluationService()
    eval_before = evaluation_service.analyze_position(board.fen())

    #Классифицируем ход пользователя
    move_type = classify_move(board, move)

    #Обновляем статистику ходов
    if move_type == 'first_line':
        game.first_line_moves += 1
    elif move_type == 'second_line':
        game.second_line_moves += 1
    elif move_type == 'third_line':
        game.third_line_moves += 1
    else:  # bad_move
        game.bad_moves += 1
    game.total_moves += 1

    #Выполняем ход игрока (убираем лишний push!)
    game.moves = append_single_move_to_pgn(str(game.moves), move, board)

    #Получаем оценку позиции после хода
    eval_after = evaluation_service.analyze_position(board.fen())

    #Вычисляем дельты между оценками
    worsened_params = analyze_deltas(eval_before, eval_after)
    feedback_messages = generate_feedback(worsened_params)

    #Обновляем рейтинг игрока
    first_line_pct = game.first_line_moves / game.total_moves * 100
    second_line_pct = game.second_line_moves / game.total_moves * 100
    third_line_pct = game.third_line_moves / game.total_moves * 100
    bad_moves_pct = game.bad_moves / game.total_moves * 100

    predicted_rating = int(predict_user_rating(
        first_line_pct, second_line_pct, third_line_pct, bad_moves_pct
    ))

    player = db.query(Player).filter(Player.id == game.player_id).first()
    if player:
        player.rating = predicted_rating

    #Обновляем уровень движка и выполняем его ход
    engine_elo = update_engine_level(predicted_rating)
    engine_level = (engine_elo - 500) // 100
    evaluation_service.process.stdin.write(f"setoption name Skill Level value {engine_level}\n")
    evaluation_service.process.stdin.flush()

    engine_move = get_best_move(board)
    game.moves = append_single_move_to_pgn(str(game.moves), engine_move, board)

    #Сохраняем изменения в базе данных
    db.commit()
    db.refresh(game)
    db.refresh(player)

    #Возвращаем результат
    return {
        "game_id": game.id,
        "player_move": user_move,
        "engine_move": engine_move.uci(),
        "engine_rating": engine_elo,
        "new_player_rating": player.rating if player else None,
        "fen": board.fen(),
        "evaluation_before": eval_before.total_evaluation,
        "evaluation_after": eval_after.total_evaluation,
        "worsened_params": worsened_params,
        "feedback_messages": feedback_messages
    }





# Функция завершения матча
def finish_match_service(match_id: int, db: Session):
    # Ищем матч в базе данных
    game = db.query(Game).filter(Game.id == match_id).first()
    board = restore_board_from_pgn(game.moves)
    if not game:
        logger.error('Match not found')
        raise HTTPException(status_code=404, detail="Match not found")
    # Обновляем статус игры
    player_color = game.player_color  # 'white' или 'black'

    # Определяем результат на основе текущего состояния доски и цвета игрока
    if board.is_checkmate():
        if player_color == 'white':
            # Игрок играет белыми
            if not board.turn:
                game.result = "win"  # Мат и ход чёрных — победа игрока
            else:
                game.result = "loss"  # Мат и ход белых — победа движка
        else:
            # Игрок играет чёрными
            if board.turn:
                game.result = "win"  # Мат и ход белых — победа игрока
            else:
                game.result = "loss"  # Мат и ход чёрных — победа движка
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        game.result = "draw"  # Ничья
    else:
        game.result = "unfinished"  # Если игра завершена до мата/ничьей

    # Обновляем статус игры и дату завершения
    game.status = "finished"
    game.end_date = datetime.now()


    # Устанавливаем дату завершения
    game.end_date = datetime.now()

    # Ищем игрока, связанного с матчем
    player = db.query(Player).filter(Player.id == game.player_id).first()

    if player:
        # # Добавляем PGN игры в список игр игрока
        # player.games.append(game.moves)

        db.commit()  # Сохраняем изменения в базе данных
    db.commit()
    return {"message": "Match finished", "player_id": player.id, "result": game.result}


def update_match_service(match_id: int, new_moves: str, db: Session):
    match = db.query(Game).filter(Game.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.moves = new_moves
    db.commit()
    return match



def get_all_matches_service(db: Session):
    """
    Получить список всех матчей из базы данных с указанием ID игрока.
    """
    matches = db.query(Game).all()
    return [{"match_id": match.id, "player_id": match.player_id, "moves": match.moves} for match in matches]


def delete_all_matches_service(db: Session):
    # Получаем все матчи из базы
    matches = db.query(Game).all()

    # Если матчей нет, возвращаем сообщение
    if not matches:
        return {"message": "No matches found in the database."}

    # Удаляем все матчи
    for match in matches:
        db.delete(match)

    # Сохраняем изменения в базе данных
    db.commit()

    return {"message": "All matches have been deleted."}
