from turtle import Turtle


class Ball(Turtle):
    STARTING_MOVE_DISTANCE = 10
    STARTING_MOVE_SPEED = 0.1
    SPEED_MULTIPLIER = 0.9
    TOP_WALL = 280
    BOTTOM_WALL = -280
    LEFT_PADDLE_BOUNCE_X = -330
    RIGHT_PADDLE_BOUNCE_X = 330

    def __init__(self):
        super().__init__()
        self.color("white")
        self.shape("circle")
        self.penup()
        self.x_move = self.STARTING_MOVE_DISTANCE
        self.y_move = self.STARTING_MOVE_DISTANCE
        self.move_speed = self.STARTING_MOVE_SPEED

    def move(self):
        new_x = self.xcor() + self.x_move
        new_y = self.ycor() + self.y_move
        self.goto(new_x, new_y)

    def bounce_y(self):
        if self.ycor() > self.TOP_WALL:
            self.sety(self.TOP_WALL)
        elif self.ycor() < self.BOTTOM_WALL:
            self.sety(self.BOTTOM_WALL)
        self.y_move *= -1

    def bounce_x(self):
        self.x_move *= -1
        self.move_speed *= self.SPEED_MULTIPLIER

    def bounce_off_paddle(self):
        if self.x_move > 0:
            self.setx(self.RIGHT_PADDLE_BOUNCE_X)
        else:
            self.setx(self.LEFT_PADDLE_BOUNCE_X)
        self.bounce_x()

    def reset_position(self):
        self.goto(0, 0)
        self.move_speed = self.STARTING_MOVE_SPEED
        self.x_move *= -1
        self.y_move = self.STARTING_MOVE_DISTANCE if self.y_move > 0 else -self.STARTING_MOVE_DISTANCE
