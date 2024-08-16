from typing import Hashable

import pandas as pd


class FinancialAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.df = df

        self.df["transaction_time"] = pd.to_datetime(self.df["transaction_time"])
        self.df.set_index("transaction_time", inplace=True)

    def get_monthly_category_spending_df(self) -> pd.DataFrame:
        return (
            self.df.groupby([pd.Grouper(freq="MS"), "category"])["amount_gbp"]
            .sum()
            .unstack(fill_value=0)
        )

    def get_week_df(self, year: int, week_number: int) -> pd.DataFrame:
        self.df["year"] = self.df.index.isocalendar().year
        self.df["week"] = self.df.index.isocalendar().week

        specific_week_df = self.df[
            (self.df["year"] == year) & (self.df["week"] == week_number)
        ]
        return specific_week_df

    def get_month_df(self, year_month: str) -> pd.DataFrame:
        return self.df.loc[year_month]

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
        average_expenses = self.df.resample(period)["amount_gbp"].sum()[1:-1].mean()
        return average_expenses

    def get_diff_between_periods(
        self, recent_period: pd.DataFrame, older_period: pd.DataFrame
    ) -> float:

        recent_period_expense = self.get_total_expense(recent_period)
        older_period_expense = self.get_total_expense(older_period)

        difference = recent_period_expense - older_period_expense

        return difference
