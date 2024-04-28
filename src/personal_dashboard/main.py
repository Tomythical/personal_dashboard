import csv
import io
import logging

from loguru import logger
from telegram import File, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .backend.database import SqlConnections
from .config import ALLOWED_USER_IDS, TOKEN

# TODO: Replace with loguru
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def csv_decoder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if str(message.from_user.id) in ALLOWED_USER_IDS:
        csv_file: File = await message.effective_attachment.get_file()
        logging.info(csv_file)

        # Read the file into memory
        csv_buffer = io.BytesIO()
        await csv_file.download_to_memory(csv_buffer)
        csv_buffer.seek(0)

        # Convert CSV bytes into a list of strings for each row
        csv_text: str = csv_buffer.read().decode("utf-8")
        csv_list: list = list(csv.reader(csv_text.splitlines()))

        SqlConnections.upsert_transaction(conn, csv_list)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Received"
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    conn = SqlConnections.sql_connect()
    csv_handler = MessageHandler(filters.Document.FileExtension("csv"), csv_decoder)

    application.add_handler(csv_handler)
    logging.info("Polling")
    application.run_polling()
