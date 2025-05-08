import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
PIXELDRAIN_API_KEY = os.getenv("PIXELDRAIN_API_KEY")

def upload_to_pixeldrain(file_path):
    with open(file_path, 'rb') as f:
        headers = {"Authorization": f"Bearer {PIXELDRAIN_API_KEY}"}
        response = requests.post("https://pixeldrain.com/api/file", files={"file": f}, headers=headers)

    if response.status_code == 200:
        file_id = response.json().get("id")
        return f"https://pixeldrain.com/u/{file_id}"
    else:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Handle file upload from Telegram
    if message.document:
        document = message.document
        file = await document.get_file()
        file_path = f"./{document.file_name}"
        await file.download_to_drive(file_path)

        link = upload_to_pixeldrain(file_path)
        os.remove(file_path)

        if link:
            await message.reply_text(f"Your permanent download link:\n{link}")
        else:
            await message.reply_text("Upload to PixelDrain failed.")

    # Handle link message (URL-based upload)
    elif message.text and message.text.startswith("http"):
        try:
            # Get file name from URL
            file_url = message.text.strip()
            file_name = file_url.split("/")[-1].split("?")[0]
            file_path = f"./{file_name}"

            # Download the file from the URL
            r = requests.get(file_url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            link = upload_to_pixeldrain(file_path)
            os.remove(file_path)

            if link:
                await message.reply_text(f"Uploaded from URL!\nPermanent link:\n{link}")
            else:
                await message.reply_text("Upload to PixelDrain failed.")

        except Exception as e:
            await message.reply_text(f"Error downloading or uploading file:\n{str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.run_polling()
