import csv

import functions_framework
import httpx
from loguru import logger

from .backend.database import SqlConnections
from .config import ALLOWED_USER_IDS, TELEGRAM_BOT_TOKEN

# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org"


@functions_framework.http
def telegram_webhook(request):
    """Entry point for Telegram webhook."""
    # Parse the incoming request data
    if request.method != "POST":
        return "Only POST requests are allowed", 405

    update = request.get_json()

    if not update or "message" not in update:
        logger.error(f"No message in update")
        return "No message in update", 400

    user_id = update["message"]["from"]["id"]
    first_name = update["message"]["from"]["first_name"]
    last_name = update["message"]["from"]["last_name"]
    chat_id = update["message"]["chat"]["id"]

    if str(user_id) != ALLOWED_USER_IDS:
        logger.error(f"Unapproved user: {first_name} {last_name}. Update: {update}")
        return f"Unapproved user: {first_name} {last_name}", 403

    # Check if the message contains a document (file)
    if "document" not in update["message"]:
        send_msg(chat_id, "Please provide a csv file")
        return "No document provided", 200

    document = update["message"]["document"]

    # Check if the file is a CSV
    if (
        document["mime_type"] != "text/csv"
        and document["mime_type"] != "text/comma-separated-values"
    ):
        send_msg(
            chat_id,
            f"Please provide a .csv file. Current file type is {document['mime_type']}",
        )
        return "Document must be of .csv type", 200

    file_id = document["file_id"]

    # Download the file from Telegram
    try:
        file_path = get_file_path(file_id)

        csv_url = f"{TELEGRAM_API_URL}/file/bot{TOKEN}/{file_path}"

        file_name = document["file_name"]
        download_file(csv_url, file_name)
        update_db(f"/tmp/{file_name}")
        send_msg(chat_id, "Transactions Processed")
        return f"{file_name} downloaded", 200

    except Exception as e:
        send_msg(chat_id, e)
        return "Failed to process file", 500


def get_file_path(file_id):
    """Get the file path for the given file_id."""
    url = f"{TELEGRAM_API_URL}/bot{TOKEN}/getFile?file_id={file_id}"
    logger.debug(f"Getting file id from url: {url}")
    try:
        response = httpx.get(url)
        response.raise_for_status()
        file_path = response.json()["result"]["file_path"]
        logger.debug(f"Retrieved file_path: {file_path}")
        return file_path
    except httpx.HTTPError as exc:
        logger.error(
            f"Failed to get file path from {exc.request.url!r}. Error: {response.text}"
        )
        raise exc


def download_file(url, file_name):
    """Download the file from the given URL."""
    try:
        logger.debug(f"Attemping to download file from url: {url}")
        response = httpx.get(url)
        response.raise_for_status()
        with open(f"/tmp/{file_name}", "wb") as f:
            f.write(response.content)
        logger.debug(f"File {file_name} downloaded successfully")
        return file_name
    except httpx.HTTPError as exc:
        logger.error(
            f"Failed to download file from {exc.request.url!r}. Error: {response.text}"
        )
        raise exc


def send_msg(chat_id, text):
    try:
        response = httpx.get(
            f"{TELEGRAM_API_URL}/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}"
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(
            f"Failed to send message using {exc.request.url!r}. Error: {response.text}"
        )
        raise exc


def update_db(file_path):
    try:
        with open(file_path) as csv_file_object:
            csv_list = list(csv.reader(csv_file_object))
        conn = SqlConnections.sql_connect()
        SqlConnections.upsert_transaction(conn, csv_list)
        conn.close()
    except FileNotFoundError as e:
        logger.error(f"Could not find csv file. {e}")
        raise e
    except Exception as e:
        logger.error(f"Failed to interact with Database")
        raise e
