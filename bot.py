import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputFile
import requests

# ======================
TOKEN = "8693061713:AAFTcWKRtPlJJudYVrfU38aM7byIednW-eM"
# ======================

# Temporary storage for user states
user_files = {}

# /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to Public Rename Bot!\n\n"
        "📤 Send me any file or video.\n"
        "✏️ I will ask new file name and resend without buttons/caption.\n"
        "Enjoy!"
    )

# Handle file/video upload
def handle_file(update: Update, context: CallbackContext):
    message = update.message
    chat_id = message.chat.id

    # Get the file_id
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    else:
        update.message.reply_text("❌ Please send a valid file or video.")
        return

    # Save state
    user_files[chat_id] = file_id
    update.message.reply_text(
        "✏️ Send me the new file name with extension.\n"
        "Example: movie.mp4 or file.zip"
    )

# Handle rename
def rename_file(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if chat_id not in user_files:
        return

    new_name = update.message.text.strip()
    file_id = user_files[chat_id]

    # Download file
    file = context.bot.get_file(file_id)
    file_path = os.path.join("/tmp", new_name)
    file.download(custom_path=file_path)

    # Send file back
    with open(file_path, "rb") as f:
        context.bot.send_document(chat_id=chat_id, document=f, caption="✅ File renamed!")

    # Remove temp file
    os.remove(file_path)
    del user_files[chat_id]

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document | Filters.video, handle_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, rename_file))

    print("🚀 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
