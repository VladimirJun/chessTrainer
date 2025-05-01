import chess

def analyze_position(fen):
    board = chess.Board(fen)

    # Подсчитываем количество фигур на доске
    piece_map = board.piece_map()
    piece_count = len(piece_map)
    king_count = sum(1 for piece in piece_map.values() if piece.piece_type == chess.KING)

    # Проверка на пустую доску
    if piece_count == 0:
        return "На доске должны быть хоть какие-то фигуры."

    # Проверка на наличие обоих королей
    if king_count < 2:
        return "Эта позиция невозможна, у каждой из сторон должен быть король."

    # Проверка на голых королей (ничья)
    if piece_count == 2 and king_count == 2:
        return ("Эта позиция — ничья, так как на доске остались только два короля. "
                "Два короля не могут поставить друг другу мат, поэтому партия заканчивается.")

    return "Позиция корректна, можно продолжать игру."