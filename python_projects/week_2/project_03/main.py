from pathlib import Path
from turtle import Screen

from food import Food
from scoreboard import Scoreboard
from snake import Snake


SCREEN_SIZE = 600
BACKGROUND_COLOR = "black"
GAME_TITLE = "My Snake Game"
FRAME_DELAY = 0.1
FRAME_DELAY_MS = int(FRAME_DELAY * 1000)
FOOD_COLLISION_DISTANCE = 15
WALL_BOUNDARY = 280
TAIL_COLLISION_DISTANCE = 10
HIGH_SCORE_PATH = Path(__file__).with_name("high_score.txt")


screen = Screen()
screen.setup(width=SCREEN_SIZE, height=SCREEN_SIZE)
screen.bgcolor(BACKGROUND_COLOR)
screen.title(GAME_TITLE)
screen.tracer(0)

snake = Snake()
food = Food()
scoreboard = Scoreboard(HIGH_SCORE_PATH)
game_is_on = True


def restart_game():
    global game_is_on
    if game_is_on:
        return
    snake.reset()
    food.refresh()
    scoreboard.reset()
    game_is_on = True
    run_game()


def end_game():
    global game_is_on
    game_is_on = False
    scoreboard.game_over()


def run_game():
    if not game_is_on:
        return

    screen.update()
    snake.move()

    if snake.head.distance(food) < FOOD_COLLISION_DISTANCE:
        food.refresh()
        snake.extend()
        scoreboard.increase_score()

    if snake.hit_wall(WALL_BOUNDARY) or snake.hit_tail(TAIL_COLLISION_DISTANCE):
        end_game()
        return

    screen.ontimer(run_game, FRAME_DELAY_MS)

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")
screen.onkey(restart_game, "r")
screen.onkey(restart_game, "R")

run_game()

screen.exitonclick()
