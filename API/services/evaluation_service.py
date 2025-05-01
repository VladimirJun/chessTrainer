import subprocess
import os
import configparser as conf
import chess
from API.assistant.evaluation import Evaluation
from API.assistant.assistant_messages import analyze_deltas, generate_feedback


class EvaluationService:
    """Сервис для анализа позиции и расчета ухудшений оценки."""

    def __init__(self):
        """Инициализация сервиса и запуск движка Stockfish."""
        config = conf.RawConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.properties')
        config.read(config_path)

        self.engine_path = config.get("Main", "EngineStr")
        self.process = self.start_engine()

    def start_engine(self):
        """Запускает движок Stockfish."""
        return subprocess.Popen(
            self.engine_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

    def send_command(self, cmd: str):
        """Отправляет команду движку."""
        self.process.stdin.write(cmd + "\n")
        self.process.stdin.flush()

    def read_response(self):
        """Читает ответ движка."""
        output = []
        while True:
            line = self.process.stdout.readline().strip()
            if line == "":
                break
            output.append(line)
        return output

    def analyze_position(self, fen: str) -> Evaluation:
        """Запрашивает детализированный анализ текущей позиции."""
        self.send_command(f"position fen {fen}")
        self.send_command("eval")
        eval_output = self.read_response()

        evaluation = Evaluation()
        evaluation.update_from_stockfish(eval_output)
        return evaluation

    def analyze_move(self, fen_before: str, move: chess.Move) -> dict:
        """
        Выполняет анализ позиции до и после хода.
        1) Получает оценку до хода.
        2) Применяет ход и получает новую оценку.
        3) Считает разницу параметров и формирует сообщения.
        """

        # 1️⃣ Анализ до хода
        eval_before = self.analyze_position(fen_before)

        # 2️⃣ Применение хода
        board = chess.Board(fen_before)
        board.push(move)
        fen_after = board.fen()

        # 3️⃣ Анализ после хода
        eval_after = self.analyze_position(fen_after)

        # 4️⃣ Вычисляем ухудшения
        worsened_params = analyze_deltas(eval_before, eval_after)
        feedback_messages = generate_feedback(worsened_params)

        return {
            "evaluation_before": eval_before,
            "evaluation_after": eval_after,
            "worsened_params": worsened_params,
            "feedback_messages": feedback_messages
        }

    def stop_engine(self):
        """Завершает работу движка Stockfish."""
        self.send_command("quit")
        self.process.terminate()
