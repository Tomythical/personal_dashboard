import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def financial_analysis(df, exclude_holiday=False):
    key_figures = {}
    df["transaction_time"] = pd.to_datetime(df["transaction_time"])
    df.set_index("transaction_time", inplace=True)

    if exclude_holiday:
        df = df[df["category"] != "Holiday"]
    # Identify the top expense categories
    top_expenses = (
        df.groupby("category")["amount_gbp"].sum().sort_values(ascending=False)
    )

    # Calculate average monthly income and expenses
    monthly_expenses = df.resample("ME")["amount_gbp"].sum().mean()

    key_figures["Top Expense Categories"] = {
        category: f"£{amount:,.2f}" for category, amount in top_expenses.head().items()
    }
    key_figures["Average Monthly Expenses"] = f"£{monthly_expenses:,.2f}"
    return key_figures
