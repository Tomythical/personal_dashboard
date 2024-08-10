from datetime import datetime as dt
from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.personal_dashboard.backend.database import SqlConnections
from src.personal_dashboard.backend.financial_analysis import FinancialAnalysis


class Figures:
    def __init__(
        self,
        df: pd.DataFrame,
        finance_analyzer: FinancialAnalysis,
        exclude_holiday=True,
    ):
        self.df = df
        self.exclude_holiday = exclude_holiday
        if self.exclude_holiday:
            self.df = self.df[self.df["category"] != "Holiday"]
        self.finance_analyzer = finance_analyzer

    def category_spending_pie_chart(self):

        category_expenses = (
            self.df.groupby("category")["amount_gbp"].sum().abs().reset_index()
        )

        fig = px.pie(
            category_expenses,
            values="amount_gbp",
            names="category",
            color_discrete_sequence=px.colors.sequential.RdBu,
            width=700,
            height=300,
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig)

    def top_category_spending_table(self):
        # Display top expense categories in a table

        df_reset = self.df.reset_index(drop=True)
        expenses_df = pd.DataFrame(
            list(self.finance_analyzer.get_top_expense_categories(df_reset).items()),
            columns=["Category", "Amount"],
        )
        st.markdown("")
        st.markdown("")
        st.table(expenses_df)


class PageComponents:

    def __init__(self, df: pd.DataFrame, exclude_holiday=False) -> None:
        self.df = df
        self.exclude_holiday = exclude_holiday
        if self.exclude_holiday:
            self.df = self.df[self.df["category"] != "Holiday"]

        self.finance_analyzer = FinancialAnalysis(self.df)

    def title(self):
        st.title("My Local AI Finance Insighter")
        st.markdown(
            "**A personalized and secure approach to analyzing financial data, providing insights and recommendations tailored to individual needs.**"
        )

    def last_week(self):
        last_week_df = self.finance_analyzer.get_last_week_df()
        col1, col2, col3 = st.columns(3)

        average_weekly_expense = self.finance_analyzer.get_average_expense("W")

        last_week_expense = self.finance_analyzer.get_total_expense(last_week_df)
        last_week_top_expense_amount, last_month_top_expense_description = (
            self.finance_analyzer.get_top_expense_and_description(last_week_df)
        )
        percentage_diff_last_two_weeks = (
            self.finance_analyzer.get_percentage_diff_between_last_two_weeks()
        )
        col1.metric(
            label="Average Weekly Expense",
            value=f"£{average_weekly_expense:,.2f}",
        )
        col2.metric(
            label="Last Week Total Expense",
            value=f"£{last_week_expense:,.2f}",
            delta=f"{percentage_diff_last_two_weeks:,.2f}% from week before",
            delta_color="inverse",
        )
        col3.metric(
            label="Last Week Top Expense",
            value=f"£{last_week_top_expense_amount:,.2f}",
            delta=last_month_top_expense_description,
            delta_color="off",
        )
        st.divider()
        # # Display top expense categories in a table
        col1, col2 = st.columns(2)
        last_week_figures = Figures(last_week_df, self.finance_analyzer)

        with col1:
            st.markdown(
                "<h4 style='text-align: left; color: white;'>Top Expenses by Category</h4>",
                unsafe_allow_html=True,
            )
            last_week_figures.top_category_spending_table()
        with col2:
            st.markdown(
                "<h4 style='text-align: left; color: white;'>Percentage of Expenses by Category</h4>",
                unsafe_allow_html=True,
            )
            last_week_figures.category_spending_pie_chart()

    def last_month(self):
        last_month_df = self.finance_analyzer.get_last_month_df()
        col1, col2, col3 = st.columns(3)

        average_monthly_expense = self.finance_analyzer.get_average_expense("ME")
        last_month_expense = self.finance_analyzer.get_total_expense(last_month_df)
        last_month_top_expense_amount, last_month_top_expense_description = (
            self.finance_analyzer.get_top_expense_and_description(last_month_df)
        )
        percentage_diff_last_two_months = (
            self.finance_analyzer.get_percentage_diff_between_last_two_months()
        )
        col1.metric(
            label="Average Monthly Expense",
            value=f"£{average_monthly_expense:,.2f}",
        )
        col2.metric(
            label="Last Month Total Expense",
            value=f"£{last_month_expense:,.2f}",
            delta=f"{percentage_diff_last_two_months:,.2f}% from month before",
            delta_color="inverse",
        )
        col3.metric(
            label="Last Month Top Expense",
            value=f"£{last_month_top_expense_amount:,.2f}",
            delta=last_month_top_expense_description,
            delta_color="off",
        )
        st.divider()
        # # Display top expense categories in a table
        col1, col2 = st.columns(2)
        last_month_figures = Figures(last_month_df, self.finance_analyzer)

        with col1:
            st.markdown(
                "<h4 style='text-align: left; color: white;'>Top Expenses by Category</h4>",
                unsafe_allow_html=True,
            )
            last_month_figures.top_category_spending_table()
        with col2:
            st.markdown(
                "<h4 style='text-align: left; color: white;'>Percentage of Expenses by Category</h4>",
                unsafe_allow_html=True,
            )
            last_month_figures.category_spending_pie_chart()

    def budget_analysis(self):
        pass

    def stats(self):
        pass


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
    components.title()

    last_week = get_last_week_dates()
    last_month = (pd.Period(dt.now(), "M") - 1).strftime("%B")
    tab1, tab2, tab3, tab4 = st.tabs(
        [f"Last Week: {last_week}", f"Last Month: {last_month}", "Stats", "Budget"]
    )
    with tab1:
        components.last_week()
    with tab2:
        components.last_month()


if __name__ == "__main__":
    conn = SqlConnections.sql_connect()
    transactions = SqlConnections.get_all_transactions_as_table(conn)
    SqlConnections.sql_disconnect(conn)
    streamlit_app(transactions, exclude_holiday=True)
