import os

import httpx
import pandas as pd
import psycopg
from dotenv import load_dotenv
from loguru import logger

YONDER = "yonder_transactions"
load_dotenv()


class SqlConnections:
    def sql_connect() -> psycopg.Connection:
        """Connect to a SQL server

        :return connection: Global database connection
        """

        try:
            SqlConnections.download_ca_cert()
            conn = psycopg.connect(os.getenv("DATABASE_URL_PSYCOPG"))
            return conn
        except Exception as e:
            logger.error("database connection failed")
            logger.error(e)
            return

    def download_ca_cert():
        dest_dir = os.path.join(os.getenv("HOME"), ".postgresql")
        dest_file = os.path.join(dest_dir, "root.crt")

        # Create directories if they don't exist
        os.makedirs(dest_dir, exist_ok=True)

        # Check if the file already exists
        if os.path.exists(dest_file):
            logger.debug(f"File already exists at {dest_file}")
        else:
            # Download the file
            try:
                with httpx.stream("GET", os.getenv("DATABASE_CA_CERT_URL")) as response:
                    response.raise_for_status()  # Check if the request was successful

                    # Write the file to the destination
                    with open(dest_file, "wb") as file:
                        for chunk in response.iter_bytes():
                            file.write(chunk)

                logger.debug(f"File downloaded and saved to {dest_file}")

            except httpx.HTTPStatusError as exc:
                raise exc(f"Failed to download file: {exc.response.status_code}")
            except Exception as e:
                raise e()

    def sql_disconnect(conn: psycopg.Connection):
        logger.info(f"Closing connection to SQL database.")
        conn.close()

    def upsert_transaction(conn: psycopg.Connection, csv_list: list[str]):

        with conn.cursor() as cur:
            for row in csv_list[1:]:
                transaction_time = row[0]
                description = row[1]
                amount_gbp = float(row[2])
                amount_charged_ccy = float(row[3])
                currency = row[4]
                category = row[5]
                debit_or_credit = row[6]
                postcode = row[7]

                logger.debug(
                    f"{transaction_time=}, {description=}, {amount_gbp=}, {amount_charged_ccy=}, {currency=}, {category=}, {debit_or_credit=}, {postcode=}"
                )
                cur.execute(
                    f"INSERT INTO {YONDER}(transaction_time, description, amount_gbp, amount_ccy, currency, category, debit_or_credit, postcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (transaction_time) DO NOTHING",
                    (
                        transaction_time,
                        description,
                        amount_gbp,
                        amount_charged_ccy,
                        currency,
                        category,
                        debit_or_credit,
                        postcode,
                    ),
                )

            conn.commit()

    def get_all_transactions_as_table(conn: psycopg.Connection) -> pd.DataFrame:

        with conn.cursor() as cur:
            query = f"SELECT * FROM {YONDER}"
            cur.execute(query)

            rows = cur.fetchall()

            colnames = [desc[0] for desc in cur.description]

            df = pd.DataFrame(rows, columns=colnames)

        return df
