import random
word_list = ["coffee", "mountain", "playlist"]

chosen_word = random.choice(word_list)
print("Welcome to Hangman: Week 1 Edition.")
print("Today's words are pulled from a more everyday vibe.")

display = []
for letter in chosen_word:
    display.append("_")

lives = 6
guessed_letters = []
game_over = False

while not game_over:
    print(f"\nWord: {' '.join(display)}")
    print(f"Lives left: {lives}")

    if guessed_letters:
        print(f"Guessed letters: {', '.join(guessed_letters)}")

    guess = input("Guess a letter for the mystery word: ").lower()

    if len(guess) != 1 or not guess.isalpha():
        print("Please enter a single letter.")
        continue

    if guess in guessed_letters:
        print("You already tried that letter.")
        continue

    guessed_letters.append(guess)

    if guess in chosen_word:
        print("Nice, that letter is in there.")
        for position in range(len(chosen_word)):
            if chosen_word[position] == guess:
                display[position] = guess
    else:
        lives -= 1
        print("Nope, not this one.")

    if "_" not in display:
        game_over = True
        print(f"\nYou win. The word was '{chosen_word}'.")

    if lives == 0:
        game_over = True
        print(f"\nOut of lives. The word was '{chosen_word}'.")
