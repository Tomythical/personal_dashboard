from datetime import datetime as dt

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.personal_dashboard.backend.financial_analysis import (
    SpendingAnalysis,
    Stats,
    TransactionPeriod,
)
from src.personal_dashboard.frontend.figures import Figures


class PageComponents:

    def __init__(self, df: pd.DataFrame, exclude_holiday=False) -> None:
        self.df = df
        self.exclude_holiday = exclude_holiday
        if self.exclude_holiday:
            self.df = self.df[self.df["category"] != "Holiday"]

        self.transaction_period = TransactionPeriod(self.df.copy())

    def __get_stats(
        self, period: pd.DataFrame, older_period: pd.DataFrame, month_or_week: str
    ) -> Stats:
        average_expense = SpendingAnalysis.get_average_expense(self.df, month_or_week)
        total_expense = SpendingAnalysis.get_total_expense(period)
        top_expense_amount, top_expense_description = (
            SpendingAnalysis.get_top_expense_and_description(period)
        )
        diff_between_two_periods = SpendingAnalysis.get_diff_between_periods(
            period, older_period
        )
        top_expense_categories = SpendingAnalysis.get_top_expense_categories(
            period
        ).items()

        return Stats(
            average_expense,
            total_expense,
            top_expense_amount,
            top_expense_description,
            diff_between_two_periods,
            top_expense_categories,
        )

    def __metrics_row(self, stats: Stats, month_or_week: str):
        col1, col2, col3 = st.columns(3)
        col1.metric(
            label=f"Average {month_or_week}ly Expense",
            value=f"£{stats.average_expense:,.2f}",
        )

        sign = "-" if stats.diff_between_two_periods < 0 else "+"
        col2.metric(
            label=f"Total Expense for {month_or_week}",
            value=f"£{stats.total_expense:,.2f}",
            delta=f"{sign} £{abs(stats.diff_between_two_periods):,.2f} from {month_or_week.lower()} before",
            delta_color="inverse",
        )

        col3.metric(
            label=f"Top Expense for {month_or_week}",
            value=f"£{stats.top_expense_amount:,.2f}",
            delta=stats.top_expense_description,
            delta_color="off",
        )
        st.divider()

    def __figures_row(
        self,
        stats: Stats,
        period_df: pd.DataFrame,
        category_spending_each_period_df: pd.DataFrame,
        month_or_week: str,
    ):
        col1, col2 = st.columns(2)
        with col1:
            Figures.top_category_spending_table(stats.top_expense_categories)
        with col2:
            Figures.category_spending_pie_chart(period_df)

        st.divider()

        Figures.category_spending_over_time_stacked_bar(
            category_spending_each_period_df, month_or_week
        )

    def weekly_view(self, chosen_datetime: dt):
        chosen_iso = chosen_datetime.isocalendar()
        week_df = self.transaction_period.get_week_df(chosen_iso.year, chosen_iso.week)

        week_before_iso = chosen_datetime - relativedelta(weeks=1)
        week_before_df = self.transaction_period.get_week_df(
            week_before_iso.year, week_before_iso.week
        )

        category_spending_each_week_df = (
            self.transaction_period.get_periodic_category_spending_df("W-MON")
        )

        stats = self.__get_stats(week_df, week_before_df, "W")
        self.__metrics_row(stats, "Week")
        self.__figures_row(stats, week_df, category_spending_each_week_df, "Week")

    def monthly_view(self, chosen_datetime: dt):
        year_month_str = chosen_datetime.strftime("%Y-%m")
        month_df = self.transaction_period.get_month_df(year_month_str)

        try:
            month_before_str = (chosen_datetime - relativedelta(months=1)).strftime(
                "%Y-%m"
            )
            month_before_df = self.transaction_period.get_month_df(month_before_str)
        except KeyError:
            month_before_df = month_df

        category_spending_each_month_df = (
            self.transaction_period.get_periodic_category_spending_df("MS")
        )

        stats = self.__get_stats(month_df, month_before_df, "ME")
        self.__metrics_row(stats, "Month")
        self.__figures_row(stats, month_df, category_spending_each_month_df, "Month")
