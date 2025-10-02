import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="💰 Personal Expense Tracker", layout="centered")
st.title("💰 Personal Expense Tracker")
st.write("Fill in your expenses and financial details to get a smart summary.")

# Use a form to keep input tidy
with st.form("expense_form"):
    st.markdown("### 📅 Timeframe")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", date.today())
    with col2:
        end_date = st.date_input("To Date", date.today())

    st.markdown("### 💵 Income & Goals")
    income = st.number_input("Monthly Income", min_value=0, step=1000)
    savings_goal = st.number_input("Savings Goal (Optional)", min_value=0, step=100)
    debt = st.number_input("Debt / EMI (Optional)", min_value=0, step=100)

    st.markdown("### 🏷 Expense Categories")
    housing = st.number_input("🏠 Housing", min_value=0, step=100)
    food = st.number_input("🍔 Food & Groceries", min_value=0, step=50)
    transportation = st.number_input("🚗 Transportation", min_value=0, step=50)
    utilities = st.number_input("🔌 Utilities & Bills", min_value=0, step=50)
    entertainment = st.number_input("🎬 Entertainment", min_value=0, step=50)
    healthcare = st.number_input("💊 Healthcare", min_value=0, step=50)
    shopping = st.number_input("🛍️ Shopping & Lifestyle", min_value=0, step=50)
    education = st.number_input("📚 Education", min_value=0, step=50)
    savings = st.number_input("📈 Savings/Investments", min_value=0, step=100)
    misc = st.number_input("🔖 Miscellaneous", min_value=0, step=50)

    submit = st.form_submit_button("📤 Generate Summary")

if submit:
    # Build the expense string
    expense_str = f"""
Timeframe: {start_date} to {end_date}
Monthly Income: {income}
Savings Goal: {savings_goal}
Debt/EMI: {debt}

Expenses:
Housing: {housing}
Food & Groceries: {food}
Transportation: {transportation}
Utilities & Bills: {utilities}
Entertainment: {entertainment}
Healthcare: {healthcare}
Shopping & Lifestyle: {shopping}
Education: {education}
Savings/Investments: {savings}
Miscellaneous: {misc}
"""

    # Call FastAPI backend
    payload = {"expenses": expense_str}
    response = requests.post("https://personal-expense-tracker-backend-latest-3.onrender.com/summarize", json=payload)

    if response.status_code == 200:
        summary = response.json()["summary"]
        st.success("✅ Summary generated!")
        st.markdown("### 📊 Expense Summary")
        # Render the summary with markdown so headings, bullets, bold, etc. show correctly
        st.markdown(summary, unsafe_allow_html=True)
    else:
        st.error(f"❌ Failed to get summary from backend. Status: {response.status_code}, Details: {response.text}")
