import time
from tkinter import TclError
from turtle import Screen, Terminator

from car_manager import CarManager
from player import Player
from scoreboard import Scoreboard

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FRAME_DELAY = 0.1
COLLISION_DISTANCE = 20


def create_screen():
    game_screen = Screen()
    game_screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    game_screen.title("Turtle Crossing")
    game_screen.tracer(0)
    return game_screen


def bind_controls(game_screen, move_player_handler, restart_handler, close_handler):
    game_screen.listen()
    game_screen.onkey(move_player_handler, "Up")
    game_screen.onkey(restart_handler, "r")
    game_screen.onkey(close_handler, "Escape")


def player_hit_car(player_obj, car_manager_obj):
    return any(car.distance(player_obj) < COLLISION_DISTANCE for car in car_manager_obj.all_cars)


screen = create_screen()

player = Player()
car_manager = CarManager()
scoreboard = Scoreboard()
game_is_on = True
game_over = False


def restart_game():
    global game_is_on, game_over
    if not game_over:
        return
    player.showturtle()
    player.go_to_start()
    car_manager.reset()
    scoreboard.reset()
    game_is_on = True
    game_over = False


def close_game():
    global game_is_on
    game_is_on = False
    try:
        screen.bye()
    except (Terminator, TclError):
        pass


def move_player():
    if game_is_on:
        player.go_up()


bind_controls(screen, move_player, restart_game, close_game)

while True:
    try:
        time.sleep(FRAME_DELAY)
        screen.update()
        if not game_is_on:
            continue

        car_manager.create_car()
        car_manager.move_cars()

        if player_hit_car(player, car_manager):
            game_is_on = False
            game_over = True
            scoreboard.game_over()

        if player.is_at_finish_line():
            player.go_to_start()
            car_manager.level_up()
            scoreboard.increase_level()
    except (Terminator, TclError):
        break

try:
    screen.exitonclick()
except (Terminator, TclError):
    pass
