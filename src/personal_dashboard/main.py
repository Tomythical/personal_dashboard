import csv
import logging
from pathlib import Path

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
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Processing File"
        )
        csv_file: File = await message.effective_attachment.get_file()
        logging.debug(f"Attached File: {csv_file}")

        logging.info("Downloading file")
        await csv_file.download_to_drive(f"/tmp/{csv_file.file_unique_id}")
        with open(f"/tmp/{csv_file.file_unique_id}") as csv_file_object:
            csv_list = list(csv.reader(csv_file_object))

        SqlConnections.upsert_transaction(conn, csv_list)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Transactions Processed"
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    conn = SqlConnections.sql_connect()
    csv_handler = MessageHandler(filters.Document.FileExtension("csv"), csv_decoder)

    application.add_handler(csv_handler)
    logging.info("Polling")
    application.run_polling()
