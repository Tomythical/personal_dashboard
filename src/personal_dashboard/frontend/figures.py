import pandas as pd
import plotly.express as px
import streamlit as st


class Figures:

    @staticmethod
    def category_spending_pie_chart(df: pd.DataFrame):
        st.markdown(
            "<h4 style='text-align: left; color: white;'>Percentage of Expenses by Category</h4>",
            unsafe_allow_html=True,
        )

        category_expenses = (
            df.groupby("category")["amount_gbp"].sum().abs().reset_index()
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

    @staticmethod
    def top_category_spending_table(df: pd.DataFrame):
        # Display top expense categories in a table
        st.markdown(
            "<h4 style='text-align: left; color: white;'>Top Expenses by Category</h4>",
            unsafe_allow_html=True,
        )
        expenses_df = pd.DataFrame(
            list(df),
            columns=["Category", "Amount"],
        )
        st.markdown("")
        st.markdown("")
        st.table(expenses_df)

    @staticmethod
    def category_spending_over_time_stacked_bar(df: pd.DataFrame):
        st.markdown(
            "<h4 style='text-align: left; color: white;'>Monthly Expenses over Time</h4>",
            unsafe_allow_html=True,
        )
        fig = px.bar(
            df,
            x="transaction_time",
            y=df.columns[1:],  # Exclude the 'transaction_time' column
            labels={"value": "Amount (GBP)", "transaction_time": "Month"},
            color_discrete_sequence=px.colors.qualitative.Dark2,
        )

        # Step 4: Display in Streamlit
        st.plotly_chart(fig)
