import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace 'YOUR_BOT_TOKEN' with the token from BotFather
TOKEN = "8114811061:AAEmPsQxjyMvZd6c4fa_puyPcIWrbZoZCa8"

DOWNLOAD_PATH = "downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

async def download_media(update: Update, context: CallbackContext):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("Please send a valid video link.")
        return

    await update.message.reply_text("Downloading... Please wait.")

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
        'writedescription': True,
        'writesubtitles': True,
        'writeinfojson': True,
        'format': 'bestvideo+bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = f"{DOWNLOAD_PATH}/{info['title']}.mp4"
            audio_path = f"{DOWNLOAD_PATH}/{info['title']}.mp3"
            caption_file = f"{DOWNLOAD_PATH}/{info['title']}.description"

        # Send Video
        with open(video_path, "rb") as video:
            await update.message.reply_video(video)

        # Send Caption
        if os.path.exists(caption_file):
            with open(caption_file, "r") as caption:
                await update.message.reply_text(f"Caption:\n{caption.read()}")

        # Extract and send audio
        ydl_opts_audio = {
            'format': 'bestaudio',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([url])

        with open(audio_path, "rb") as audio:
            await update.message.reply_audio(audio)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        
# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I'm your bot. How can I help you?")

# Echo messages
async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(update.message.text)

def main():
    app = Application.builder().token(TOKEN).build()

    # Command handler
    app.add_handler(CommandHandler("start", start))

    # Message handler (echoes user input)
 #   app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))

    # Start polling for updates
    app.run_polling()

if __name__ == "__main__":
    main()

