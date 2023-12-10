from telegram import Update, MenuButtonCommands
from telegram.ext import Application, CommandHandler, ContextTypes

from dotenv import dotenv_values
config = dotenv_values(".env")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def send_creamy(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    await context.bot.send_photo(chat_id, open('assets/creamy.jpg', 'rb'))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    if context.job_queue.get_jobs_by_name(str(chat_id)):
        await update.message.reply_text(f"Creamy knows you are waiting for his message, he'll get back to you!!")
    else:
        await update.message.reply_text(f"Hi! {update.effective_user.first_name}")
        await update.message.reply_text(f"I will send you a message every day to check up on you")
        await update.message.reply_text(f"You can opt out at any time by using /stop, and restart using /start")
        context.job_queue.run_repeating(send_creamy, chat_id=chat_id, name=str(chat_id), interval=86399, first=10)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    
    if remove_job_if_exists(str(chat_id), context):
        await update.message.reply_text(f"Sorry to see you go :((")
        await update.message.reply_text(f"To restart, just type /start")
    else:
        await update.message.reply_text(f"You are not on Creamy's list. To be on it, type /start")
    


if __name__ == "__main__":

    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config["BOT_TOKEN"]).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
