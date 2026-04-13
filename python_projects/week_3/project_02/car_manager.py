import random
from turtle import Turtle

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 5
SPAWN_CHANCE = 6
STARTING_X = 320
OFFSCREEN_X = -340
LANES = (-250, -210, -170, -130, -90, -50, -10, 30, 70, 110, 150, 190, 230, 270)


class CarManager:
    def __init__(self):
        self.all_cars = []
        self.car_speed = STARTING_MOVE_DISTANCE

    def create_car(self):
        random_chance = random.randint(1, SPAWN_CHANCE)
        if random_chance == 1:
            new_car = Turtle("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)
            new_car.penup()
            new_car.color(random.choice(COLORS))
            new_car.goto(STARTING_X, random.choice(LANES))
            self.all_cars.append(new_car)

    def move_cars(self):
        for car in self.all_cars:
            car.backward(self.car_speed)
        self._remove_offscreen_cars()

    def level_up(self):
        self.car_speed += MOVE_INCREMENT

    def reset(self):
        for car in self.all_cars:
            car.hideturtle()
        self.all_cars.clear()
        self.car_speed = STARTING_MOVE_DISTANCE

    def _remove_offscreen_cars(self):
        remaining_cars = []
        for car in self.all_cars:
            if car.xcor() < OFFSCREEN_X:
                car.hideturtle()
            else:
                remaining_cars.append(car)
        self.all_cars = remaining_cars
