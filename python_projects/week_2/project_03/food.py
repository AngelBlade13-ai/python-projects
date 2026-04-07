import random
from turtle import Turtle


FOOD_COLOR = "blue"
FOOD_SIZE = 0.5
FOOD_BOUNDS = 280


class Food(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=FOOD_SIZE, stretch_wid=FOOD_SIZE)
        self.color(FOOD_COLOR)
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        random_x = random.randint(-FOOD_BOUNDS, FOOD_BOUNDS)
        random_y = random.randint(-FOOD_BOUNDS, FOOD_BOUNDS)
        self.goto(random_x, random_y)
