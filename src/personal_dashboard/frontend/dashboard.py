from datetime import datetime as dt
from datetime import timedelta

import pandas as pd
import streamlit as st

from src.personal_dashboard.backend.database import SqlConnections
from src.personal_dashboard.frontend.page_components import PageComponents


def get_last_week_dates():
    current_date = dt.now()
    start_of_current_week = current_date - timedelta(days=current_date.weekday())
    start_of_last_week = start_of_current_week - timedelta(weeks=1)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    formatted_dates = f"{start_of_last_week.day:02}-{end_of_last_week.day:02}"
    return formatted_dates


def streamlit_app(df: pd.DataFrame, exclude_holiday=False):
    st.set_page_config(layout="wide")
    components = PageComponents(df, exclude_holiday)
    st.title("My Finance Dashboard")
    last_week = get_last_week_dates()
    last_month = (pd.Period(dt.now(), "M") - 1).strftime("%B")
    tab1, tab2, tab3, tab4 = st.tabs(
        [f"Last Week: {last_week}", f"Last Month: {last_month}", "Stats", "Budget"]
    )
    with tab1:
        components.weekly_view()
    with tab2:
        components.monthly_view()


if __name__ == "__main__":
    conn = SqlConnections.sql_connect()
    transactions = SqlConnections.get_all_transactions_as_table(conn)
    SqlConnections.sql_disconnect(conn)
    streamlit_app(transactions, exclude_holiday=True)
