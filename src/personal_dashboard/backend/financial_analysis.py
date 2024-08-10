from typing import Hashable, Set

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


class FinancialAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.df = df

        self.df["transaction_time"] = pd.to_datetime(self.df["transaction_time"])
        self.df.set_index("transaction_time", inplace=True)

    def __get_last_day_of_last_month(self) -> pd.Timestamp:
        current_date = pd.Timestamp("now")
        first_day_of_current_month = current_date.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - pd.Timedelta(days=1)
        return last_day_of_last_month

    def get_last_month_df(self) -> pd.DataFrame:
        last_day_of_last_month = self.__get_last_day_of_last_month()
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        df_last_month = self.df[
            (self.df.index >= first_day_of_last_month)
            & (self.df.index <= last_day_of_last_month)
        ]

        return df_last_month

    def get_last_week_df(self) -> pd.DataFrame:
        current_date = pd.Timestamp("now")
        last_monday = current_date - pd.to_timedelta(
            current_date.weekday() + 7, unit="D"
        )
        last_sunday = last_monday + pd.Timedelta(days=6)
        last_monday = last_monday.replace(hour=0, minute=0, second=0)
        last_sunday = last_sunday.replace(hour=23, minute=59, second=59)
        return self.df[(self.df.index >= last_monday) & (self.df.index <= last_sunday)]

    def get_two_months_before_df(self) -> pd.DataFrame:
        last_day_of_last_month = self.__get_last_day_of_last_month()
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        last_day_of_month_before_last = first_day_of_last_month - pd.Timedelta(days=1)
        first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)

        df_month_before_last = self.df[
            (self.df.index >= first_day_of_month_before_last)
            & (self.df.index <= last_day_of_month_before_last)
        ]

        return df_month_before_last

    def get_two_weeks_before_df(self) -> pd.DataFrame:
        current_date = pd.Timestamp("now")
        last_monday = current_date - pd.to_timedelta(
            current_date.weekday() + 7, unit="D"
        )
        two_weeks_before_monday = last_monday - pd.Timedelta(days=7)
        two_weeks_before_sunday = two_weeks_before_monday + pd.Timedelta(days=6)

        return self.df[
            (self.df.index >= two_weeks_before_monday)
            & (self.df.index <= two_weeks_before_sunday)
        ]

    def get_total_expense(self, df: pd.DataFrame):
        last_month_expense = df["amount_gbp"].sum()
        return last_month_expense

    def get_top_expense_and_description(self, df: pd.DataFrame):
        top_expense_row = df.loc[df["amount_gbp"].idxmax()]
        top_expense_amount = top_expense_row["amount_gbp"]
        top_expense_description = top_expense_row["description"]
        return top_expense_amount, top_expense_description

    def get_top_expense_categories(self, df: pd.DataFrame) -> dict[Hashable, str]:
        category_spending = df.groupby("category")["amount_gbp"].sum()
        top_categories = category_spending.sort_values(ascending=False)
        top_categories_expense_amount = {
            category: f"£{amount:,.2f}"
            for category, amount in top_categories.head().items()
        }
        return top_categories_expense_amount

    def get_average_expense(self, period: str):
        average_expenses = self.df.resample(period)["amount_gbp"].sum().mean()
        return average_expenses

    def get_percentage_diff_between_last_two_months(self):
        last_month_df = self.get_last_month_df()
        two_months_ago_df = self.get_two_months_before_df()

        last_month_expense = self.get_total_expense(last_month_df)
        two_months_ago_expense = self.get_total_expense(two_months_ago_df)

        percentage_difference = (
            (last_month_expense - two_months_ago_expense) / two_months_ago_expense
        ) * 100

        return percentage_difference

    def get_percentage_diff_between_last_two_weeks(self):
        last_week_df = self.get_last_week_df()
        two_weeks_ago_df = self.get_two_weeks_before_df()

        last_week_expense = self.get_total_expense(last_week_df)
        two_weeks_ago_expense = self.get_total_expense(two_weeks_ago_df)

        percentage_difference = (
            (last_week_expense - two_weeks_ago_expense) / two_weeks_ago_expense
        ) * 100

        return percentage_difference
