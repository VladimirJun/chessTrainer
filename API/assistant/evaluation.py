import re


class Evaluation:
    """Класс для хранения оценки позиции Stockfish."""

    def __init__(self):
        # Все параметры инициализируются нулями
        self.material_mg_white = 0.0
        self.material_eg_white = 0.0
        self.material_mg_black = 0.0
        self.material_eg_black = 0.0

        self.pawns_mg_white = 0.0
        self.pawns_eg_white = 0.0
        self.pawns_mg_black = 0.0
        self.pawns_eg_black = 0.0

        self.knights_mg_white = 0.0
        self.knights_eg_white = 0.0
        self.knights_mg_black = 0.0
        self.knights_eg_black = 0.0

        self.bishops_mg_white = 0.0
        self.bishops_eg_white = 0.0
        self.bishops_mg_black = 0.0
        self.bishops_eg_black = 0.0

        self.rooks_mg_white = 0.0
        self.rooks_eg_white = 0.0
        self.rooks_mg_black = 0.0
        self.rooks_eg_black = 0.0

        self.queens_mg_white = 0.0
        self.queens_eg_white = 0.0
        self.queens_mg_black = 0.0
        self.queens_eg_black = 0.0

        self.mobility_mg_white = 0.0
        self.mobility_eg_white = 0.0
        self.mobility_mg_black = 0.0
        self.mobility_eg_black = 0.0

        self.king_safety_mg_white = 0.0
        self.king_safety_eg_white = 0.0
        self.king_safety_mg_black = 0.0
        self.king_safety_eg_black = 0.0

        self.threats_mg_white = 0.0
        self.threats_eg_white = 0.0
        self.threats_mg_black = 0.0
        self.threats_eg_black = 0.0

        self.passed_pawns_mg_white = 0.0
        self.passed_pawns_eg_white = 0.0
        self.passed_pawns_mg_black = 0.0
        self.passed_pawns_eg_black = 0.0

        self.space_mg_white = 0.0
        self.space_eg_white = 0.0
        self.space_mg_black = 0.0
        self.space_eg_black = 0.0

        self.initiative_white = 0.0
        self.initiative_black = 0.0

        self.total_evaluation = 0.0

    def update_from_stockfish(self, eval_output):
        """Парсит ответ движка и обновляет параметры класса."""
        pattern = re.compile(
            r"(\w[\w\s]+)\s*\|\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*\|\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)")

        for line in eval_output:
            match = pattern.match(line)
            if match:
                term, mg_white, eg_white, mg_black, eg_black = match.groups()
                term = term.strip().lower().replace(" ", "_")

                # Назначаем значения
                if term == "material":
                    self.material_mg_white, self.material_eg_white, self.material_mg_black, self.material_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "pawns":
                    self.pawns_mg_white, self.pawns_eg_white, self.pawns_mg_black, self.pawns_eg_black = map(float,
                                                                                                             [mg_white,
                                                                                                              eg_white,
                                                                                                              mg_black,
                                                                                                              eg_black])
                elif term == "knights":
                    self.knights_mg_white, self.knights_eg_white, self.knights_mg_black, self.knights_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "bishops":
                    self.bishops_mg_white, self.bishops_eg_white, self.bishops_mg_black, self.bishops_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "rooks":
                    self.rooks_mg_white, self.rooks_eg_white, self.rooks_mg_black, self.rooks_eg_black = map(float,
                                                                                                             [mg_white,
                                                                                                              eg_white,
                                                                                                              mg_black,
                                                                                                              eg_black])
                elif term == "queens":
                    self.queens_mg_white, self.queens_eg_white, self.queens_mg_black, self.queens_eg_black = map(float,
                                                                                                                 [
                                                                                                                     mg_white,
                                                                                                                     eg_white,
                                                                                                                     mg_black,
                                                                                                                     eg_black])
                elif term == "mobility":
                    self.mobility_mg_white, self.mobility_eg_white, self.mobility_mg_black, self.mobility_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "king_safety":
                    self.king_safety_mg_white, self.king_safety_eg_white, self.king_safety_mg_black, self.king_safety_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "threats":
                    self.threats_mg_white, self.threats_eg_white, self.threats_mg_black, self.threats_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "passed":
                    self.passed_pawns_mg_white, self.passed_pawns_eg_white, self.passed_pawns_mg_black, self.passed_pawns_eg_black = map(
                        float, [mg_white, eg_white, mg_black, eg_black])
                elif term == "space":
                    self.space_mg_white, self.space_eg_white, self.space_mg_black, self.space_eg_black = map(float,
                                                                                                             [mg_white,
                                                                                                              eg_white,
                                                                                                              mg_black,
                                                                                                              eg_black])
                elif term == "initiative":
                    self.initiative_white, self.initiative_black = float(mg_white), float(mg_black)
            self.total_evaluation = (
                    self.material_mg_white + self.material_eg_white - self.material_mg_black - self.material_eg_black +
                    self.mobility_mg_white + self.mobility_mg_white - self.mobility_mg_black - self.mobility_eg_black +
                    self.king_safety_mg_white + self.king_safety_eg_white - self.king_safety_mg_black - self.king_safety_eg_black +
                    self.threats_mg_white + self.threats_eg_white - self.threats_mg_black - self.threats_eg_black +
                    self.space_mg_white + self.space_eg_white - self.space_mg_black - self.space_eg_black +
                    self.initiative_white - self.initiative_black
            )



