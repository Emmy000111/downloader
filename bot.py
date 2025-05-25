import os
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Download options for yt-dlp
YDL_OPTS = {
    'format': 'mp4',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

if not os.path.exists('downloads'):
    os.makedirs('downloads')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video link from TikTok, Twitter, Snapchat, Facebook, and I'll download it for you!")


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    await update.message.reply_text("Downloading your video... Please wait.")

    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

        # Send video file back
        with open(filepath, 'rb') as video_file:
            await context.bot.send_video(chat_id=chat_id, video=InputFile(video_file))

        # Clean up file after sending
        os.remove(filepath)

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await update.message.reply_text("Sorry, I couldn't download the video. Please check the link and try again.")


def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))

    print("Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()
