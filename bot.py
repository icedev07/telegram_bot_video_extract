import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

TOKEN = "8114811061:AAEmPsQxjyMvZd6c4fa_puyPcIWrbZoZCa8"
DOWNLOAD_PATH = "downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def sanitize_filename(filename):
    """Remove non-standard characters from the filename."""
    return re.sub(r'[\\/*?:"<>|]', '', filename)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me a video link, and I'll download the video, caption, and audio.")

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

            # Sanitize the title for safe file naming
            safe_title = sanitize_filename(info['title'])

            video_path = f"{DOWNLOAD_PATH}/{safe_title}.mp4"
            caption_file = f"{DOWNLOAD_PATH}/{safe_title}.description"

        # Send Video
        if os.path.exists(video_path):
            with open(video_path, "rb") as video:
                await update.message.reply_video(video)

        # Send Caption
        if os.path.exists(caption_file):
            with open(caption_file, "r") as caption:
                await update.message.reply_text(f"Caption:\n{caption.read()}")

        # Extract and send audio
        audio_path = f"{DOWNLOAD_PATH}/{safe_title}.mp3"

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

        if os.path.exists(audio_path):
            with open(audio_path, "rb") as audio:
                await update.message.reply_audio(audio)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("I don't understand that command.")

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start bot
    app.run_polling()

if __name__ == "__main__":
    main()
