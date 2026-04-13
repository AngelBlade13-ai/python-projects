import time
from tkinter import TclError
from turtle import Screen, Terminator

from ball import Ball
from paddle import Paddle
from scoreboard import Scoreboard

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FRAME_DELAY = 1 / 60
TOP_WALL = 280
BOTTOM_WALL = -280
RIGHT_PADDLE_X = 350
LEFT_PADDLE_X = -350
RIGHT_MISS_X = 380
LEFT_MISS_X = -380
PADDLE_COLLISION_X = 320
PADDLE_COLLISION_DISTANCE = 50


def create_screen():
    game_screen = Screen()
    game_screen.bgcolor("black")
    game_screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    game_screen.title("Pong")
    game_screen.tracer(0)
    return game_screen


def bind_controls(game_screen, pressed_keys, close_handler):
    game_screen.listen()
    game_screen.onkeypress(lambda: set_key_state(pressed_keys, "Up", True), "Up")
    game_screen.onkeyrelease(lambda: set_key_state(pressed_keys, "Up", False), "Up")
    game_screen.onkeypress(lambda: set_key_state(pressed_keys, "Down", True), "Down")
    game_screen.onkeyrelease(lambda: set_key_state(pressed_keys, "Down", False), "Down")
    game_screen.onkeypress(lambda: set_key_state(pressed_keys, "w", True), "w")
    game_screen.onkeyrelease(lambda: set_key_state(pressed_keys, "w", False), "w")
    game_screen.onkeypress(lambda: set_key_state(pressed_keys, "s", True), "s")
    game_screen.onkeyrelease(lambda: set_key_state(pressed_keys, "s", False), "s")
    game_screen.onkey(close_handler, "Escape")


def set_key_state(pressed_keys, key, is_pressed):
    pressed_keys[key] = is_pressed


def move_paddles(pressed_keys, right_paddle_obj, left_paddle_obj):
    if pressed_keys["Up"]:
        right_paddle_obj.go_up()
    if pressed_keys["Down"]:
        right_paddle_obj.go_down()
    if pressed_keys["w"]:
        left_paddle_obj.go_up()
    if pressed_keys["s"]:
        left_paddle_obj.go_down()


def ball_hits_wall(game_ball):
    return game_ball.ycor() > TOP_WALL or game_ball.ycor() < BOTTOM_WALL


def ball_hits_paddle(game_ball, right_paddle_obj, left_paddle_obj):
    hits_right_paddle = (
        game_ball.distance(right_paddle_obj) < PADDLE_COLLISION_DISTANCE
        and game_ball.xcor() > PADDLE_COLLISION_X
        and game_ball.x_move > 0
    )
    hits_left_paddle = (
        game_ball.distance(left_paddle_obj) < PADDLE_COLLISION_DISTANCE
        and game_ball.xcor() < -PADDLE_COLLISION_X
        and game_ball.x_move < 0
    )
    return hits_right_paddle or hits_left_paddle


def award_point(game_ball, game_scoreboard, is_left_player):
    game_ball.reset_position()
    if is_left_player:
        game_scoreboard.l_point()
    else:
        game_scoreboard.r_point()

    if game_scoreboard.has_winner():
        game_scoreboard.game_over()
        return True

    return False

screen = create_screen()
right_paddle = Paddle((RIGHT_PADDLE_X, 0))
left_paddle = Paddle((LEFT_PADDLE_X, 0))
ball = Ball()
scoreboard = Scoreboard()
game_is_on = True
keys_pressed = {"Up": False, "Down": False, "w": False, "s": False}
last_ball_move = time.perf_counter()


def close_game():
    global game_is_on
    game_is_on = False
    try:
        screen.bye()
    except (Terminator, TclError):
        pass


bind_controls(screen, keys_pressed, close_game)

while game_is_on:
    try:
        time.sleep(FRAME_DELAY)
        move_paddles(keys_pressed, right_paddle, left_paddle)
        screen.update()

        current_time = time.perf_counter()
        if current_time - last_ball_move >= ball.move_speed:
            ball.move()
            last_ball_move = current_time

        if ball_hits_wall(ball):
            ball.bounce_y()

        if ball_hits_paddle(ball, right_paddle, left_paddle):
            ball.bounce_off_paddle()

        if ball.xcor() > RIGHT_MISS_X:
            game_is_on = not award_point(ball, scoreboard, is_left_player=True)
            last_ball_move = time.perf_counter()

        if ball.xcor() < LEFT_MISS_X:
            game_is_on = not award_point(ball, scoreboard, is_left_player=False)
            last_ball_move = time.perf_counter()
    except (Terminator, TclError):
        game_is_on = False
        break

try:
    screen.exitonclick()
except (Terminator, TclError):
    pass
