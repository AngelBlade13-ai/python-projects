from pathlib import Path
from random import choice, randint, shuffle
from tkinter import Button, Canvas, END, Entry, Label, PhotoImage, Tk, messagebox

try:
    import pyperclip
except ImportError:
    pyperclip = None

WINDOW_PADDING = 50
CANVAS_SIZE = 200
DEFAULT_EMAIL = "you@example.com"
DATA_FILE = Path(__file__).with_name("data.txt")
LOGO_FILE = Path(__file__).with_name("logo.png")

LETTERS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
NUMBERS = list("0123456789")
SYMBOLS = list("!#$%&()*+")


def copy_with_pyperclip(text):
    if pyperclip is None:
        return False
    pyperclip.copy(text)
    return True


class PasswordManagerApp:
    def __init__(self):
        self.window = Tk()
        self.window.title("Password Manager")
        self.window.config(padx=WINDOW_PADDING, pady=WINDOW_PADDING)

        self.canvas = Canvas(width=CANVAS_SIZE, height=CANVAS_SIZE, highlightthickness=0)
        self._create_logo()
        self.canvas.grid(row=0, column=1)

        Label(text="Website:").grid(row=1, column=0)
        Label(text="Email/Username:").grid(row=2, column=0)
        Label(text="Password:").grid(row=3, column=0)

        self.website_entry = Entry(width=35)
        self.website_entry.grid(row=1, column=1, columnspan=2)
        self.website_entry.focus()

        self.email_entry = Entry(width=35)
        self.email_entry.grid(row=2, column=1, columnspan=2)
        self.email_entry.insert(0, DEFAULT_EMAIL)

        self.password_entry = Entry(width=21)
        self.password_entry.grid(row=3, column=1)

        Button(
            text="Generate Password",
            width=14,
            command=self.generate_password,
        ).grid(row=3, column=2)

        Button(
            text="Add",
            width=36,
            command=self.save_password,
        ).grid(row=4, column=1, columnspan=2)

    def generate_password(self):
        password_letters = [choice(LETTERS) for _ in range(randint(8, 10))]
        password_symbols = [choice(SYMBOLS) for _ in range(randint(2, 4))]
        password_numbers = [choice(NUMBERS) for _ in range(randint(2, 4))]

        password_list = password_letters + password_symbols + password_numbers
        shuffle(password_list)
        password = "".join(password_list)

        self.password_entry.delete(0, END)
        self.password_entry.insert(0, password)
        self._copy_to_clipboard(password)

    def save_password(self):
        website = self.website_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not website or not password:
            messagebox.showinfo(
                title="Oops",
                message="Please make sure you haven't left any fields empty.",
            )
            return

        is_ok = messagebox.askokcancel(
            title=website,
            message=f"These are the details entered:\nEmail: {email}\nPassword: {password}\nSave?",
        )
        if not is_ok:
            return

        with DATA_FILE.open("a", encoding="utf-8") as data_file:
            data_file.write(f"{website} | {email} | {password}\n")

        self.website_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.website_entry.focus()

    def _create_logo(self):
        if LOGO_FILE.exists():
            logo_image = PhotoImage(file=str(LOGO_FILE))
            self.canvas.create_image(CANVAS_SIZE // 2, CANVAS_SIZE // 2, image=logo_image)
            self.canvas.image = logo_image
            return

        self.canvas.create_text(
            CANVAS_SIZE // 2,
            CANVAS_SIZE // 2,
            text="MyPass",
            font=("Arial", 28, "bold"),
        )

    def _copy_to_clipboard(self, text):
        if copy_with_pyperclip(text):
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        self.window.update()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = PasswordManagerApp()
    app.run()
