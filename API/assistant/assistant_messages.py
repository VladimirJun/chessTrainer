from API.assistant.evaluation import Evaluation
def analyze_deltas(eval_before: Evaluation, eval_after: Evaluation):
    """Анализ ухудшения параметров после хода."""
    worsened_params = {}

    for attr in vars(eval_before):
        before_value = getattr(eval_before, attr)
        after_value = getattr(eval_after, attr)

        if before_value > after_value:  # Параметр ухудшился
            worsened_params[attr] = round(after_value - before_value, 2)  # Разница

    return worsened_params
def generate_feedback(worsened_params):
    """Генерирует текстовые объяснения ухудшений."""
    messages = []

    explanations = {
        "total_evaluation": "Общая оценка позиции ухудшилась, возможно, ход ослабил вашу позицию.",
        "mobility_mg_white": "Ваши фигуры стали менее мобильными, попробуйте открытые линии.",
        "mobility_mg_black": "Ваши фигуры стали менее мобильными, попробуйте открытые линии.",
        "king_safety_mg_white": "Ваш король стал менее защищён, следите за безопасностью.",
        "king_safety_mg_black": "Ваш король стал менее защищён, следите за безопасностью.",
        "threats_mg_white": "Вы упустили возможность создать угрозу для соперника.",
        "threats_mg_black": "Вы упустили возможность создать угрозу для соперника.",
        "space_mg_white": "Вы потеряли контроль над пространством, подумайте о центральных пешках.",
        "space_mg_black": "Вы потеряли контроль над пространством, подумайте о центральных пешках.",
        "initiative_white": "Вы утратили инициативу, попробуйте атаковать активнее.",
        "initiative_black": "Вы утратили инициативу, попробуйте атаковать активнее.",
    }

    worst_param = min(worsened_params,
                      key=worsened_params.get)  # Берем параметр с наибольшим ухудшением (наименьшее значение)
    worst_delta = worsened_params[worst_param]  # Значение ухудшения

    if worst_param in explanations:
        return [f"{explanations[worst_param]} (ухудшение на {worst_delta})"]

    return messages
