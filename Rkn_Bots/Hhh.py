import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import Config 

# Define choices
CHOICES = ["rock", "paper", "scissors"]

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to Rock-Paper-Scissors! Type /play to start.")

def play(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Choose: rock, paper, or scissors!")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_choice = update.message.text.lower()
    
    if user_choice not in CHOICES:
        update.message.reply_text("Invalid choice! Please choose rock, paper, or scissors.")
        return

    bot_choice = random.choice(CHOICES)
    result = determine_winner(user_choice, bot_choice)

    update.message.reply_text(f"You chose {user_choice}, I chose {bot_choice}. {result}")

def determine_winner(user_choice: str, bot_choice: str) -> str:
    if user_choice == bot_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        return "You win!"
    else:
        return "I win!"

def main():
    # Replace 'YOUR_TOKEN' with your actual bot token
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("play", play))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
