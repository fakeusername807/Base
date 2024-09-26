from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import Rkn_Bots

   async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       await update.message.reply_text("Welcome to Rock-Paper-Scissors! Type /play to start.")

   async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       await update.message.reply_text("Choose: rock, paper, or scissors!")

   async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       user_choice = update.message.text.lower()

       if user_choice not in CHOICES:
           await update.message.reply_text("Invalid choice! Please choose rock, paper, or scissors.")
           return

       bot_choice = random.choice(CHOICES)
       result = determine_winner(user_choice, bot_choice)

       await update.message.reply_text(f"You chose {user_choice}, I chose {bot_choice}. {result}")

   async def main():
       app = ApplicationBuilder().token("BOT_TOKEN").build()

       app.add_handler(CommandHandler("start", start))
       app.add_handler(CommandHandler("play", play))
       app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

       await app.run_polling()

   if __name__ == '__main__':
       import asyncio
       asyncio.run(main())
   
