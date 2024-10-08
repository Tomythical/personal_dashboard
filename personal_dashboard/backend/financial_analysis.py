from dataclasses import dataclass
from typing import Hashable

import pandas as pd


class TransactionPeriod:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_periodic_category_spending_df(self, frequency: str) -> pd.DataFrame:
        return (
            self.df.groupby([pd.Grouper(freq=frequency), "category"])["amount_gbp"]
            .sum()
            .unstack(fill_value=0)
        )

    def get_week_df(self, year: int, week_number: int) -> pd.DataFrame:
        self.df.loc[:, "year"] = self.df.index.isocalendar().year
        self.df.loc[:, "week"] = self.df.index.isocalendar().week

        specific_week_df = self.df[
            (self.df["year"] == year) & (self.df["week"] == week_number)
        ]
        return specific_week_df

    def get_month_df(self, year_month: str) -> pd.DataFrame:
        return self.df.loc[year_month]


class SpendingAnalysis:

    @staticmethod
    def get_total_expense(df: pd.DataFrame) -> float:
        last_month_expense = df["amount_gbp"].sum()
        return last_month_expense

    @staticmethod
    def get_top_expense_and_description(df: pd.DataFrame):
        top_expense_row = df.loc[df["amount_gbp"].idxmax()]
        top_expense_amount = top_expense_row["amount_gbp"]
        top_expense_description = top_expense_row["description"]
        return top_expense_amount, top_expense_description

    @staticmethod
    def get_top_expense_categories(df: pd.DataFrame) -> dict[Hashable, str]:
        category_spending = df.groupby("category")["amount_gbp"].sum()
        top_categories = category_spending.sort_values(ascending=False)
        top_categories_expense_amount = {
            category: f"£{amount:,.2f}"
            for category, amount in top_categories.head().items()
        }
        return top_categories_expense_amount

    @staticmethod
    def get_average_expense(df: pd.DataFrame, period: str) -> float:
        average_expenses = df.resample(period)["amount_gbp"].sum()[1:-1].mean()
        return average_expenses

    @staticmethod
    def get_diff_between_periods(
        recent_period: pd.DataFrame, older_period: pd.DataFrame
    ) -> float:

        recent_period_expense = SpendingAnalysis.get_total_expense(recent_period)
        older_period_expense = SpendingAnalysis.get_total_expense(older_period)

        difference = recent_period_expense - older_period_expense

        return difference


@dataclass
class Stats:
    average_expense: float
    total_expense: float
    top_expense_amount: float
    top_expense_description: str
    diff_between_two_periods: float
    top_expense_categories: dict[Hashable, str]
