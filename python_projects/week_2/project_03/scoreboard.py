from turtle import Turtle


ALIGNMENT = "center"
FONT = ("Courier", 24, "normal")
SCORE_POSITION = (0, 270)
GAME_OVER_POSITION = (0, 0)
GAME_OVER_TEXT = "GAME OVER"
RESTART_TEXT = "Press R to restart"


class Scoreboard(Turtle):
    def __init__(self, high_score_path):
        super().__init__()
        self.score = 0
        self.high_score_path = high_score_path
        self.high_score = self.load_high_score()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.goto(SCORE_POSITION)
        self.update_scoreboard()

    def load_high_score(self):
        try:
            with open(self.high_score_path, "r", encoding="utf-8") as file:
                return int(file.read().strip() or 0)
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open(self.high_score_path, "w", encoding="utf-8") as file:
            file.write(str(self.high_score))

    def update_scoreboard(self):
        self.clear()
        self.goto(SCORE_POSITION)
        self.write(
            f"Score: {self.score}  High Score: {self.high_score}",
            align=ALIGNMENT,
            font=FONT,
        )

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.update_scoreboard()
        self.goto(GAME_OVER_POSITION)
        self.write(f"{GAME_OVER_TEXT}\n{RESTART_TEXT}", align=ALIGNMENT, font=FONT)

    def reset(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.score = 0
        self.update_scoreboard()
