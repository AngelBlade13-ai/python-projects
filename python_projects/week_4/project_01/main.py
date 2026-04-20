from pathlib import Path
from random import choice
from tkinter import Button, Canvas, PhotoImage, Tk
import csv


BACKGROUND_COLOR = "#B1DDC6"
CURRENT_CARD = {}
FLIP_TIMER = None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"
WORDS_TO_LEARN_FILE = DATA_DIR / "words_to_learn.csv"
SOURCE_WORDS_FILE = DATA_DIR / "french_words.csv"


def load_words():
    source_file = WORDS_TO_LEARN_FILE if WORDS_TO_LEARN_FILE.exists() else SOURCE_WORDS_FILE
    return read_words(source_file)


def read_words(path):
    with path.open(mode="r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def save_words(path, words):
    with path.open(mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["French", "English"])
        writer.writeheader()
        writer.writerows(words)


to_learn = load_words()


def next_card():
    global CURRENT_CARD, FLIP_TIMER

    if FLIP_TIMER is not None:
        window.after_cancel(FLIP_TIMER)
        FLIP_TIMER = None

    if not to_learn:
        CURRENT_CARD = {}
        canvas.itemconfig(card_background, image=card_front_img)
        canvas.itemconfig(card_title, text="Finished!", fill="black")
        canvas.itemconfig(card_word, text="You've learned all the words.", fill="black")
        return

    CURRENT_CARD = choice(to_learn)
    canvas.itemconfig(card_background, image=card_front_img)
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=CURRENT_CARD["French"], fill="black")
    FLIP_TIMER = window.after(3000, flip_card)


def flip_card():
    canvas.itemconfig(card_background, image=card_back_img)
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=CURRENT_CARD["English"], fill="white")


def is_known():
    if not CURRENT_CARD:
        return

    to_learn.remove(CURRENT_CARD)
    save_words(WORDS_TO_LEARN_FILE, to_learn)
    next_card()


window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

card_front_img = PhotoImage(file=str(IMAGES_DIR / "card_front.png"))
card_back_img = PhotoImage(file=str(IMAGES_DIR / "card_back.png"))
wrong_image = PhotoImage(file=str(IMAGES_DIR / "wrong.png"))
right_image = PhotoImage(file=str(IMAGES_DIR / "right.png"))

canvas = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="Title", font=("Arial", 40, "italic"))
card_word = canvas.create_text(400, 263, text="Word", font=("Arial", 60, "bold"))
canvas.grid(row=0, column=0, columnspan=2)

unknown_button = Button(image=wrong_image, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

known_button = Button(image=right_image, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=1)

next_card()

window.mainloop()
