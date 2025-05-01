import cv2
import numpy as np
from tensorflow_chessbot.tensorflow_learn_cnn import makePrediction

def extract_fen_from_video(video_path: str, threshold: float = 0.05):
    """
    Анализирует видео, извлекает шахматные позиции (FEN) с таймингами.

    :param video_path: Путь к видеофайлу
    :param threshold: Порог изменения позиций (чем выше, тем меньше дубликатов)
    :return: Список [(тайминг в секундах, FEN-строка)]
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    prev_fen = None
    fen_timeline = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Текущее время в секундах

        try:
            fen = makePrediction(frame)  # Распознаем шахматную позицию
            if fen and (prev_fen is None or fen != prev_fen):
                fen_timeline.append((time_sec, fen))
                prev_fen = fen  # Обновляем последнюю распознанную позицию
        except Exception as e:
            print(f"[Ошибка] {e} на {time_sec} сек.")

    cap.release()
    return fen_timeline


#Пример вызова функции
video_file = ""
fen_data = extract_fen_from_video(video_file)

# Выводим результат
for time, fen in fen_data:
    print(f"{time:.2f} сек → {fen}")
