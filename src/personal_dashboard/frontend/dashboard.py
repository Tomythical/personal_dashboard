import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.personal_dashboard.backend.database import SqlConnections
from src.personal_dashboard.backend.financial_analysis import financial_analysis


def plot_category_wise_spending_analysis(df: pd.DataFrame, exclude_holiday=False):
    if exclude_holiday:
        df = df[df["category"] != "Holiday"]

    st.markdown("4. Category-wise Spending Analysis")
    expenses_by_category = df.groupby("category")["amount_gbp"].sum()

    expenses_by_category.plot(
        kind="pie", figsize=(10, 8), autopct="%1.1f%%", startangle=140
    )
    plt.title("Expenses Analysis")
    plt.ylabel("")  # Hide the y-label as it's unnecessary for pie charts
    # plt.savefig("data/expense_category_analysis.png", bbox_inches="tight")
    st.pyplot(plt)


def streamlit_app(df: pd.DataFrame, exclude_holiday=False):
    st.title("My Local AI Finance Insighter")
    st.markdown(
        "**A personalized and secure approach to analyzing financial data, providing insights and recommendations tailored to individual needs.**"
    )

    analysis_results = financial_analysis(df, exclude_holiday)
    results_str = ""
    # Loop through the dictionary
    for key, value in analysis_results.items():
        if isinstance(value, dict):
            # If the value is another dictionary, further iterate to get sub-keys and values
            sub_results = ", ".join(
                [f"{sub_key}: {sub_value}" for sub_key, sub_value in value.items()]
            )
            results_str += f"{key}: {sub_results}\n"
        else:
            # For direct key-value pairs, simply concatenate
            results_str += f"{key}: {value}\n"

    # Display average monthly figures
    st.subheader("Average Monthly Figures")
    col1, col2 = st.columns(2)
    col1.metric(
        label="Average Monthly Expenses",
        value=analysis_results["Average Monthly Expenses"],
    )
    col2.metric(
        label="Average Monthly Expenses",
        value=analysis_results["Average Monthly Expenses"],
    )

    # Display top expense categories in a table
    st.subheader("Top Expense Categories")
    expenses_df = pd.DataFrame(
        list(analysis_results["Top Expense Categories"].items()),
        columns=["Category", "Amount"],
    )
    st.table(expenses_df)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            plot_category_wise_spending_analysis(df, exclude_holiday)
        with col2:
            plot_category_wise_spending_analysis(df, exclude_holiday)


if __name__ == "__main__":
    conn = SqlConnections.sql_connect()
    transactions = SqlConnections.get_all_transactions_as_table(conn)
    SqlConnections.sql_disconnect(conn)
    streamlit_app(transactions, exclude_holiday=True)
