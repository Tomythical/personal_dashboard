from datetime import datetime as dt

import pandas as pd
import streamlit as st

from src.personal_dashboard.backend.database import SqlConnections
from src.personal_dashboard.backend.utils import extract_first_date, get_day_suffix
from src.personal_dashboard.frontend.page_components import PageComponents


def spending_period_filter(df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        available_years = df.index.year.unique().sort_values().tolist()
        year = st.selectbox(
            "Year",
            available_years,
        )
    with col2:
        available_months = reversed(
            df[df.index.year == year].index.month.unique().sort_values().tolist()
        )
        month_names = [
            pd.to_datetime(f"2024-{month}-01").strftime("%B")
            for month in available_months
        ]
        month = st.selectbox(
            "Month",
            month_names,
        )
    with col4:
        st.markdown("")
        st.markdown("")
        week_view_activated = st.toggle("Week View")
    with col3:
        week = None
        if week_view_activated:
            month_number = pd.to_datetime(month, format="%B").month
            df_weeks = df[(df.index.year == year) & (df.index.month == month_number)]
            weeks = reversed(df_weeks.index.to_period("W").unique())
            week_start_dates = [
                f"{week.start_time.day}{get_day_suffix(week.start_time.day)}-{week.end_time.day}{get_day_suffix(week.end_time.day)}"
                for week in weeks
                if week.start_time.month == month_number
            ]
            week = st.selectbox(
                "Week",
                week_start_dates,
            )

    st.divider()
    return (year, month, week)


def streamlit_app(df: pd.DataFrame, exclude_holiday=False):
    components = PageComponents(df, exclude_holiday)
    tab1, tab2 = st.tabs([f"Spending Analysis", "Stats"])
    with tab1:
        year, month, week = spending_period_filter(df)
        beginning_date_from_week = extract_first_date(week)
        chosen_datetime = pd.to_datetime(
            f"{year}-{month}-{beginning_date_from_week}", format="mixed"
        )
        if week is not None:
            components.weekly_view(chosen_datetime)
        else:
            components.monthly_view(chosen_datetime)


@st.cache_data(ttl="1d")
def get_transaction_df():
    conn = SqlConnections.sql_connect()
    transactions = SqlConnections.get_all_transactions_as_table(conn)
    SqlConnections.sql_disconnect(conn)
    return transactions


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    transactions = get_transaction_df()
    transactions.loc[:, "transaction_time"] = pd.to_datetime(
        transactions["transaction_time"]
    )
    transactions.set_index("transaction_time", inplace=True)

    streamlit_app(transactions, exclude_holiday=True)
