import random
import time

import pandas as pd
import psycopg
from loguru import logger

from src.personal_dashboard import config

YONDER = "yonder_transactions"


class SqlConnections:
    def sql_connect() -> psycopg.Connection:
        """Connect to a SQL server

        :return connection: Global database connection
        """

        try:
            conn = psycopg.connect(config.DATABASE_URL_PSYCOPG)
            return conn
        except Exception as e:
            logger.error("database connection failed")
            logger.error(e)
            return

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
