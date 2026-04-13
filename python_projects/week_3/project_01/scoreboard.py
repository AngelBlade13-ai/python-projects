from turtle import Turtle

WINNING_SCORE = 3


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.l_score = 0
        self.r_score = 0
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.goto(-100, 200)
        self.write(self.l_score, align="center", font=("Courier", 80, "normal"))
        self.goto(100, 200)
        self.write(self.r_score, align="center", font=("Courier", 80, "normal"))

    def l_point(self):
        self.l_score += 1
        self.update_scoreboard()

    def r_point(self):
        self.r_score += 1
        self.update_scoreboard()

    def has_winner(self):
        return self.l_score >= WINNING_SCORE or self.r_score >= WINNING_SCORE

    def winner_text(self):
        if self.l_score >= WINNING_SCORE:
            return "Left Player Wins!"
        if self.r_score >= WINNING_SCORE:
            return "Right Player Wins!"
        return ""

    def game_over(self):
        self.goto(0, 0)
        self.write(self.winner_text(), align="center", font=("Courier", 32, "normal"))
