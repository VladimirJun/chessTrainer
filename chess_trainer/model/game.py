import configparser as conf
import logging
import tkinter as tk
import os
import chess
import chess.engine
import joblib
import pandas as pd
from PIL import Image, ImageTk
from stockfish import Stockfish


from ChessAI.chess_trainer.game_analyze.chess_utils import evaluate_position

log_filename = "ServerLog.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Также вывод логов в консоль
    ]
)
logger = logging.getLogger(__name__)
# Загрузка модели и scaler
relative_path = "chess_rating_model.pkl"
# Преобразуем относительный путь в абсолютный
model_path = os.path.abspath(relative_path)

best_model = joblib.load(model_path)
scaler_path = os.path.abspath('scaler.pkl')
scaler = joblib.load(scaler_path)

# Загрузка конфигурации
config = conf.RawConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '../system_files/config.properties')
config.read(config_path)
engine_path = config.get("Main", "EngineStr")

# Инициализация движка
stockfish  = Stockfish(engine_path)


engine = chess.engine.SimpleEngine.popen_uci(engine_path)


def predict_user_rating(first_line_percentage, second_line_percentage, third_line_percentage, bad_moves_percentage):
    input_data = pd.DataFrame({
        'first_line_percentage': [first_line_percentage],
        'second_line_percentage': [second_line_percentage],
        'third_line_percentage': [third_line_percentage],
        'bad_moves_percentage': [bad_moves_percentage]
    })
    input_data_scaled = scaler.transform(input_data)
    predicted_rating = best_model.predict(input_data_scaled)
    return predicted_rating[0]


class ChessApp:
    def __init__(self, mainw):
        self.root = mainw
        self.root.title("chess_trainer GMW")
        self.root.configure(bg='#f0f0f0')  # Установка фона окна
        self.board = chess.Board()
        self.images = {}
        self.load_images()

        self.canvas = tk.Canvas(mainw, width=480, height=480)
        self.canvas.pack(pady=10)

        self.status_label = tk.Label(mainw, text="Choose your side", font='arial 12 bold', bg='#d9d9d9', fg='#333333')
        self.status_label.pack(pady=5)

        self.rating_label = tk.Label(mainw, text="Predicted Rating: N/A | Engine ELO: N/A", font='arial 12 bold',
                                     bg='#d9d9d9', fg='#333333')
        self.rating_label.pack(pady=5)

        self.surrender_button = tk.Button(mainw, text="Surrender", command=self.surrender, font='arial 12 bold',
                                          bg='#ffcccc', fg='#333333')
        self.surrender_button.pack(pady=10)

        self.canvas.bind("<Button-1>", self.click)

        self.firstLine = 0
        self.secondLine = 0
        self.thirdLine = 0
        self.badMoves = 0
        self.totalMoves = 0

        self.current_engine_elo = 500
        self.update_engine_level()

        self.side_choice_frame = tk.Frame(mainw, bg='#f0f0f0')
        self.side_choice_frame.pack(pady=10)

        self.white_button = tk.Button(self.side_choice_frame, text="Play as White", command=self.play_as_white,
                                      font='arial 12 bold', bg='#d9d9d9', fg='#333333')
        self.white_button.grid(row=0, column=0, padx=10)

        self.black_button = tk.Button(self.side_choice_frame, text="Play as Black", command=self.play_as_black,
                                      font='arial 12 bold', bg='#d9d9d9', fg='#333333')
        self.black_button.grid(row=0, column=1, padx=10)

        self.is_white_turn = None
        self.player_color = None
        self.engine_color = None
        self.is_board_flipped = False

    def load_images(self):
        image_path = config.get('Main', 'ImagePath')
        pieces = {
            'b': 'bB.png', 'k': 'bK.png', 'n': 'bN.png', 'p': 'bP.png', 'q': 'bQ.png', 'r': 'bR.png',
            'B': 'wB.png', 'K': 'wK.png', 'N': 'wN.png', 'P': 'wP.png', 'Q': 'wQ.png', 'R': 'wR.png'
        }
        for piece, filename in pieces.items():
            self.images[piece] = ImageTk.PhotoImage(
                Image.open(f"{image_path}/{filename}")
            )

    def draw_board(self):
        self.canvas.delete("all")
        for rank in range(8):
            for file in range(8):
                x1 = file * 60
                y1 = rank * 60
                x2 = x1 + 60
                y2 = y1 + 60
                color = "white" if (rank + file) % 2 == 0 else "BurlyWood"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file = square % 8
                rank = square // 8
                if self.player_color == chess.WHITE:
                    x = file * 60
                    y = (7 - rank) * 60
                else:
                    x = (7 - file) * 60
                    y = rank * 60
                piece_image = self.images.get(piece.symbol())
                if piece_image:
                    self.canvas.create_image(x, y, image=piece_image, anchor=tk.NW)

    def play_as_white(self):
        self.player_color = chess.WHITE
        self.engine_color = chess.BLACK
        self.is_white_turn = True
        self.side_choice_frame.pack_forget()
        self.status_label.config(text="Your turn")
        self.draw_board()

    def play_as_black(self):
        self.player_color = chess.BLACK
        self.engine_color = chess.WHITE
        self.is_white_turn = False
        self.side_choice_frame.pack_forget()
        self.status_label.config(text="Engine's turn")
        self.draw_board()
        self.after_user_move()

    def click(self, event):
        if self.player_color is None:
            return

        x = event.x // 60
        y = 7 - (event.y // 60)

        square = chess.square(x, y)

        if self.board.turn == self.player_color:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
            elif hasattr(self, 'selected_square'):
                move = chess.Move(self.selected_square, square)
                print(move)
                if move in self.board.legal_moves:
                    self.process_user_move(move)
                    self.after_user_move()

    def process_user_move(self, move):
        pre_move_score = evaluate_position(self.board)
        best_move_info = engine.analyse(self.board, chess.engine.Limit(time=0.5))
        best_move = best_move_info['pv'][0]
        self.board.push(best_move)
        best_move_eval = engine.analyse(self.board, chess.engine.Limit(time=0.5))['score'].relative.score(
            mate_score=10000) / 100.0
        log_msg = f"Best move: {best_move}, Evaluation: {best_move_eval:.2f}"
        logging.info(log_msg)
        self.board.pop()

        # Выполняем ход пользователя
        self.board.push(move)
        user_move_info = engine.analyse(self.board, chess.engine.Limit(time=0.5))
        user_move_eval = user_move_info['score'].relative.score(mate_score=10000) / 100.0

        # Подсчет статистики
        difference = abs(best_move_eval - user_move_eval)
        user_winning = pre_move_score >= 2.5
        if user_winning:
            if difference <= 0.6:
                self.firstLine += 1
            elif 0.6 < difference <= 1:
                self.secondLine += 1
            elif 1 < difference <= 1.5:
                self.thirdLine += 1
            else:
                self.badMoves += 1
        if not user_winning:
            if difference < 0.25:
                self.firstLine += 1

            elif 0.25 <= difference < 0.4:
                self.secondLine += 1
            elif 0.4 <= difference < 0.8:
                self.thirdLine += 1
            else:
                self.badMoves += 1
        self.totalMoves += 1
        log_msg = f"User move: {move}, Evaluation: {user_move_eval:.2f}"
        print(log_msg)  # По-прежнему выводим в консоль
        logging.info(log_msg)  # Логируем в файл

        self.draw_board()
        del self.selected_square

    def after_user_move(self):
        if self.board.is_checkmate():
            self.status_label.config(text="Checkmate")
            self.print_statistics()
            return

        # Движок делает ход только если это не первый ход в игре
        if self.board.turn == self.engine_color:
            engine_move = engine.play(self.board, chess.engine.Limit(time=1.0)).move
            self.board.push(engine_move)
            self.draw_board()

            if self.board.is_checkmate():
                self.status_label.config(text="Checkmate")
                self.print_statistics()
                return

        # Переключение очереди ходов
        self.is_white_turn = not self.is_white_turn

        # Оценка после каждого хода
        self.evaluate_game()

    def evaluate_game(self):
        if self.totalMoves == 0:
            return

        first_line_percentage = (self.firstLine / self.totalMoves) * 100
        second_line_percentage = (self.secondLine / self.totalMoves) * 100
        third_line_percentage = (self.thirdLine / self.totalMoves) * 100
        bad_moves_percentage = (self.badMoves / self.totalMoves) * 100

        predicted_rating = predict_user_rating(first_line_percentage, second_line_percentage, third_line_percentage,
                                               bad_moves_percentage)
        self.update_engine_level(predicted_rating)
        self.rating_label.config(
            text=f"Predicted Rating: {int(predicted_rating)} | Engine ELO: {self.current_engine_elo}")

    def update_engine_level(self, predicted_rating=500):
        if predicted_rating < 800:
            self.current_engine_elo = 500
        elif 800 <= predicted_rating < 1200:
            self.current_engine_elo = 1200
        elif 1100 <= predicted_rating < 1300:
            self.current_engine_elo = 1400
        elif 1300 <= predicted_rating <= 1500:
            self.current_engine_elo = 1600
        elif 1500 <= predicted_rating <= 1700:
            self.current_engine_elo = 1900
        elif 1700 < predicted_rating <= 1800:
            self.current_engine_elo = 2000
        else:
            self.current_engine_elo = 2400
        skill_level = (self.current_engine_elo - 500) // 100
        engine.configure({"Skill Level": skill_level})

    def surrender(self):
        self.status_label.config(text="You surrendered")
        self.print_statistics()

    def print_statistics(self):
        stats = (
            f"Total Moves: {self.totalMoves}",
            f"First Line Moves: {self.firstLine}",
            f"Second Line Moves: {self.secondLine}",
            f"Third Line Moves: {self.thirdLine}",
            f"Bad Moves: {self.badMoves}"
        )
        for stat in stats:
            print(stat)  # По-прежнему выводим в консоль
            logging.info(stat)  # Логируем в файл

    def mainloop(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    app.mainloop()

    engine.quit()
