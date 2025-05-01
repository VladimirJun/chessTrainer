import configparser as conf
import csv
import time

import berserk
import chess
import chess.engine
import os

config = conf.RawConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '../system_files/config.properties')

config_path = os.path.abspath(config_path)
config.read(config_path)

# Инициализация API
token = config.get("Main", "LichessToken")
session = berserk.TokenSession(token)
client = berserk.Client(session)
engine = chess.engine.SimpleEngine.popen_uci(config.get("Main", "EngineStr"))
engine.configure({"Threads": 4})  # Установка числа потоков (1-32)


def classify_move(board: chess.Board, user_move: chess.Move) -> str:
    """
    Классифицирует ход пользователя в зависимости от разницы между оценкой сделанного хода и наилучшего хода.

    Параметры:
    - board (chess.Board): текущее состояние доски
    - user_move (chess.Move): сделанный ход пользователя

    Возвращает:
    - str: класс хода ('first_line', 'second_line', 'third_line' или 'bad_move')
    """
    # Оценка текущей позиции до хода пользователя
    pre_move_eval = evaluate_position(board)

    # Оценка позиции после хода пользователя
    board.push(user_move)
    user_move_eval = evaluate_position(board)
    board.pop()

    # Находим лучший возможный ход и его оценку
    best_move_info = engine.analyse(board, chess.engine.Limit(time=0.5))
    best_move_eval = best_move_info['score'].relative.score(mate_score=10000) / 100.0

    # Считаем разницу между оценкой лучшего хода и хода пользователя
    difference = abs(best_move_eval - user_move_eval)
    is_winning_position = pre_move_eval >= 2.5

    # Классификация в зависимости от отклонения
    if is_winning_position:
        if difference <= 0.6:
            return 'first_line'
        elif 0.6 < difference <= 1:
            return 'second_line'
        elif 1 < difference <= 1.5:
            return 'third_line'
        else:
            return 'bad_move'
    else:
        if difference < 0.25:
            return 'first_line'
        elif 0.25 <= difference < 0.4:
            return 'second_line'
        elif 0.4 <= difference < 0.8:
            return 'third_line'
        else:
            return 'bad_move'


def append_single_move_to_pgn(moves: str, move: chess.Move, board: chess.Board) -> str:
    """
    Дополняет строку PGN новым ходом в формате SAN.

    Параметры:
    - moves (str): текущая строка PGN
    - move (chess.Move): объект хода
    - board (chess.Board): текущая позиция на доске до выполнения хода

    Возвращает:
    - str: обновленная строка PGN
    """
    # Определяем номер хода на основе количества уже сделанных ходов
    move_number = board.fullmove_number

    # Преобразуем ход в строку в формате SAN до выполнения хода
    move_san = board.san(move)

    # Формируем новый ход в формате PGN
    if board.turn:  # Если сейчас ход белых
        new_move = f"{move_number}. {move_san}"
    else:  # Если сейчас ход черных
        new_move = f"{move_san}"

    # Если строка PGN не пуста, добавляем пробел перед новым ходом
    if moves:
        moves += f" {new_move}"
    else:
        moves = new_move

    # Только теперь выполняем ход на доске
    board.push(move)

    return moves



def restore_board_from_pgn(moves_pgn: str) -> chess.Board:
    """
    Восстанавливает шахматную доску из строки PGN в формате SAN.

    Параметры:
    - moves_pgn (str): строка с ходами в формате PGN (SAN).

    Возвращает:
    - chess.Board: восстановленная шахматная доска.
    """
    board = chess.Board()

    # Разбиваем строку PGN на отдельные ходы по пробелу
    moves_list = moves_pgn.split()

    for move in moves_list:
        try:
            # Пропускаем номера ходов (например, "1.", "2.")
            if move.endswith('.'):
                continue
            # Преобразуем ход из SAN в объект chess.Move и выполняем его
            board.push_san(move)
        except ValueError:
            print(f"Некорректный ход в формате SAN: {move}")
            continue

    return board


# Функция для классификации хода по линии (первая, вторая, третья или плохой ход)
def update_move_statistics(move_class: str, match: dict):
    # Увеличиваем счетчики ходов в зависимости от класса хода
    if move_class == 'first_line':
        match['first_line_moves'] += 1
    elif move_class == 'second_line':
        match['second_line_moves'] += 1
    elif move_class == 'third_line':
        match['third_line_moves'] += 1
    elif move_class == 'bad_move':
        match['bad_moves'] += 1

    # Увеличиваем общее количество ходов
    match['total_moves'] += 1

    # Подсчитываем проценты для каждого типа хода
    total_moves = match['total_moves']

    # Предотвращаем деление на ноль
    if total_moves == 0:
        first_line_percentage = second_line_percentage = third_line_percentage = bad_moves_percentage = 0
    else:
        first_line_percentage = (match['first_line_moves'] / total_moves) * 100
        second_line_percentage = (match['second_line_moves'] / total_moves) * 100
        third_line_percentage = (match['third_line_moves'] / total_moves) * 100
        bad_moves_percentage = (match['bad_moves'] / total_moves) * 100

    # Возвращаем статистику в процентах
    return {
        'first_line_percentage': first_line_percentage,
        'second_line_percentage': second_line_percentage,
        'third_line_percentage': third_line_percentage,
        'bad_moves_percentage': bad_moves_percentage
    }



def evaluate_position(board, depths=(8, 12, 16)):
    #Оценивает позицию на доске с использованием шахматного движка на нескольких глубинах и усредняет результат
    scores = []
    for depth in depths:
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info['score'].relative.score(mate_score=10000) / 100
        scores.append(score)
    average_score = sum(scores) / len(scores)
    return average_score


def get_best_move(board, depth=12):
    result = engine.play(board, chess.engine.Limit(depth=depth))
    return result.move




def analyze_and_save_game(username, game, csv_writer):
    try:
        white_rating = game['players']['white']['rating']
        black_rating = game['players']['black']['rating']
        moves = game['moves'].split()

        player_color = 'white' if game['players']['white']['user']['name'].lower() == username.lower() else 'black'
        player_rating = white_rating if player_color == 'white' else black_rating
        board = chess.Board()

        # Переменные для хранения данных
        first_line_moves = 0
        second_line_moves = 0
        third_line_moves = 0
        bad_moves = 0
        total_moves = 0

        for move_index, move_san in enumerate(moves):
            is_users_move = (player_color == 'white' and move_index % 2 == 0) or (
                    player_color == 'black' and move_index % 2 != 0)

            if not is_users_move:
                board.push_san(move_san)
                continue

            try:
                move_obj = board.parse_san(move_san)
            except ValueError:
                continue

            legal_moves = list(board.legal_moves)

            if move_obj in legal_moves:
                # Оценка позиции перед ходом с усреднением по нескольким глубинам
                pre_move_score = evaluate_position(board)

                # Оценка лучшего хода
                best_move = get_best_move(board, depth=12)
                board.push(best_move)
                best_move_score = evaluate_position(board)
                board.pop()

                board.push(move_obj)
                post_move_score = evaluate_position(board)

                score_difference = post_move_score - best_move_score
                user_winning = (pre_move_score >= 2.5)

                move_classified = False

                if user_winning:
                    # Если пользователь выигрывает, смягчаем оценку ошибок
                    if score_difference <= 0.6:
                        first_line_moves += 1
                        move_classified = True
                    elif 0.6 < score_difference <= 1:
                        second_line_moves += 1
                        move_classified = True
                    elif 1 < score_difference <= 1.5:
                        third_line_moves += 1
                        move_classified = True
                    else:
                        bad_moves += 1
                        move_classified = True
                else:
                    # Если партия только началась (дебют), ужесточаем оценку
                    if move_index < 10:
                        if score_difference <= 0.25:
                            first_line_moves += 1
                            move_classified = True
                        elif 0.25 < score_difference <= 0.5:
                            second_line_moves += 1
                            move_classified = True
                        elif 0.5 < score_difference <= 0.8:
                            third_line_moves += 1
                            move_classified = True
                        else:
                            bad_moves += 1
                            move_classified = True
                    else:
                        # Оценка в середине и конце игры
                        if score_difference <= 0.2:
                            first_line_moves += 1
                            move_classified = True
                        elif 0.2 < score_difference <= 0.4:
                            second_line_moves += 1
                            move_classified = True
                        elif score_difference > 0.4 and pre_move_score * 0.5 <= post_move_score:
                            third_line_moves += 1
                            move_classified = True
                        else:
                            bad_moves += 1
                            move_classified = True

                total_moves += 1

                # Проверка на "ложные ошибки"
                if score_difference < -2.0:
                    # Если ошибка серьезная, но соперник ее не наказал
                    opponent_best_move = get_best_move(board, depth=12)
                    board.push(opponent_best_move)
                    opponent_response_score = evaluate_position(board)
                    board.pop()

                    if opponent_response_score <= post_move_score:
                        bad_moves -= 1  # Смягчаем оценку за ложную ошибку

                        # Если ход был ошибочным, но соперник не наказал, переклассифицируем его
                        if not move_classified:
                            if score_difference <= 0.2:
                                first_line_moves += 1
                            elif 0.2 < score_difference <= 0.4:
                                second_line_moves += 1
                            else:
                                third_line_moves += 1

                board.pop()  # Отменяем ход для анализа следующего хода

            board.push_san(move_san)  # Восстанавливаем исходное состояние доски

        if total_moves > 0:
            csv_writer.writerow({
                'username': username,
                'user_rating': player_rating,
                'first_line_percentage': format(first_line_moves / total_moves * 100, '.2f'),
                'second_line_percentage': format(second_line_moves / total_moves * 100, '.2f'),
                'third_line_percentage': format(third_line_moves / total_moves * 100, '.2f'),
                'bad_moves_percentage': format(bad_moves / total_moves * 100, '.2f')
            })
            print(f"Game analyzed and saved for {username}")

    except Exception as e:
        print(f"Error analyzing game for {username}: {e}")


def analyze_games(usernames, max_games, output_file='chess_data.csv'):
    with open(output_file, mode='w', newline='') as file:
        fieldnames = ['username', 'user_rating', 'first_line_percentage', 'second_line_percentage',
                      'third_line_percentage', 'bad_moves_percentage']
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for username in usernames:
            attempts = 3
            while attempts > 0:
                try:
                    games = client.games.export_by_player(username, max=max_games)
                    break
                except Exception as e:
                    attempts -= 1
                    print(f"Error fetching games for {username}, attempts left: {attempts}. Error: {e}")
                    time.sleep(5)
                    if attempts == 0:
                        continue

            for game in games:
                analyze_and_save_game(username, game, csv_writer)

    engine.quit()

def update_engine_level(predicted_rating=500):
    if predicted_rating < 800:
        current_engine_elo = 500
    elif 800 <= predicted_rating < 1200:
        current_engine_elo = 1200
    elif 1100 <= predicted_rating < 1300:
        current_engine_elo = 1400
    elif 1300 <= predicted_rating <= 1500:
        current_engine_elo = 1600
    elif 1500 <= predicted_rating <= 1700:
        current_engine_elo = 1900
    elif 1700 < predicted_rating <= 1800:
        current_engine_elo = 2000
    else:
        current_engine_elo = 2400
    skill_level = (current_engine_elo - 500) // 100
    engine.configure({"Skill Level": skill_level})
    return current_engine_elo


if __name__ == "__main__":
    usernames = ['Ucitel','Ro_ro2','BarsWm123_55','Dikaioupolis','Ali430','GelioChess','faceofmarlboro','muisback','TurtleBot','DavidsGuterBot',
                 'RootEngine','sargon','jangine','Elmichess','AshNostromo','sargon-3ply','piglet_engine',
                 'maia1','maia5','maia9','LeelaRogue','Jibbby','sargon-1ply','notropis','honzovy-sachy','Khalid2023','cerenkarablut']
    analyze_games(usernames, max_games=200)

