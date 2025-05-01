from chess import Board
from fastapi import HTTPException


def analyze_position(fen: str) -> str:
    try:
        board = Board(fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid FEN string: {str(e)}")

    pieces = board.piece_map()

    if not pieces:
        return "На доске должны быть хоть какие-то фигуры."

    kings = [piece for piece in pieces.values() if piece.symbol().lower() == 'k']

    if len(kings) < 2:
        return "Эта позиция невозможна: у каждой из сторон должен быть король."

    if len(pieces) == 2 and len(kings) == 2:
        return (
            "Это ничья, так как на доске остались только два короля. "
            "Короли не могут поставить мат друг другу, что делает позицию невозможной для выигрыша."
        )

    return "Позиция корректна, можно продолжать игру."