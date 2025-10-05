import streamlit as st
from datetime import date
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="💰 Personal Expense Tracker", layout="wide")

# ---------- Main Title ----------
st.markdown(
    """
    <div style='
        text-align: center;
        font-weight: bold;
        color: #FFFFFF;
        font-family: "Arial", sans-serif;
        margin-top:-20px;
        margin-bottom:20px;
        font-size:48px;
    '>
        💰 Personal Expense Tracker Bot
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

# ---------- Layout Columns ----------
left_col, divider_col, right_col = st.columns([0.8, 0.02, 1.3])  # left smaller than right


# ---------- LEFT COLUMN: PDF + Expense Form ----------
with left_col:
    # ---------- COMMON INCOME & GOALS ----------
    st.subheader("💵 Income & Goals", divider='grey')
    col1, col2, col3 = st.columns(3)
    with col1:
        income = st.number_input("Monthly Income", min_value=0, step=1000)
    with col2:
        savings_goal = st.number_input("Savings Goal (Optional)", min_value=0, step=100)
    with col3:
        debt = st.number_input("Debt / EMI (Optional)", min_value=0, step=100)
    
    st.write("")
    st.markdown("<p style='font-weight:bold; text-align:center; font-size:18px; margin:5px;'>Choose one out of the two options to get started !</p>", unsafe_allow_html=True)
    st.write("")

    # PDF Upload Form
    with st.form("pdf"):
        st.markdown("<p style='font-weight:bold; font-size:18px; margin:0;'>📄 Upload Paytm UPI Statement PDF</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["pdf"])
        # Placeholder for error message
        pdf_error_placeholder = st.empty()
        pdf_submit = st.form_submit_button("📤 Generate Summary from PDF")

    # OR separator
    st.markdown(
        "<div style='text-align:center; margin:10px 0; color:#aaa; font-weight:bold;'>────── OR ──────</div>",
        unsafe_allow_html=True
    )

    # Expense Form Box
    with st.form("expense_form"):
        st.markdown(
            """
            <div style='padding:15px; margin-bottom:0px;'>
                <p style='font-weight:bold; font-size:18px; margin-bottom:0px;'>💵 Fill Expense & Financial Details</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Timeframe
        st.markdown("### 📅 Timeframe")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", date.today())
        with col2:
            end_date = st.date_input("To Date", date.today())

        # Expense Categories (3 columns)
        st.markdown("### 🏷 Expense Categories")
        col1, col2, col3 = st.columns(3)
        with col1:
            housing = st.number_input("🏠 Housing", min_value=0, step=100)
            transportation = st.number_input("🚗 Transportation", min_value=0, step=50)
            entertainment = st.number_input("🎬 Entertainment", min_value=0, step=50)
            shopping = st.number_input("🛍️ Shopping & Lifestyle", min_value=0, step=50)
        with col2:
            food = st.number_input("🍔 Food & Groceries", min_value=0, step=50)
            utilities = st.number_input("🔌 Utilities & Bills", min_value=0, step=50)
            healthcare = st.number_input("💊 Healthcare", min_value=0, step=50)
            education = st.number_input("📚 Education", min_value=0, step=50)
        with col3:
            savings = st.number_input("📈 Savings/Investments", min_value=0, step=100)
            misc = st.number_input("🔖 Miscellaneous", min_value=0, step=50)

        form_submit = st.form_submit_button("📤 Generate Summary from Form")
    
    # ---------- PROCESS INPUTS INTO SESSION STATE ----------
    if pdf_submit and uploaded_file:
        try:
            # Send PDF to backend
            response = requests.post("http://127.0.0.1:8000/parse-pdf", files={"file": uploaded_file})
            if response.status_code == 200:
                data = response.json()

                if "error" in data:
                    pdf_error_placeholder.error("⚠️ Please upload the **actual Paytm UPI Monthly Statement PDF**.")
                else:
                    pdf_error_placeholder.empty()  # clear previous errors
                    st.session_state["chart_data"] = data

                # Build expense summary string
                expense_str = f"""
                Timeframe: {data['timeframe']}
                Monthly Income: {income}
                Savings Goal: {savings_goal}
                Debt/EMI: {debt}
                Total Expense: ₹{data['total_expense']}

                Categories & Amounts:
                """
                for cat, amt in data['categories'].items():
                    pct = data['percentages'].get(cat, 0)
                    expense_str += f"{cat}: ₹{amt} ({pct}%)\n"
                st.session_state["expense_summary_payload"] = expense_str
            else:
                pdf_error_placeholder.error(f"⚠️ Backend error. Status: {response.status_code}")
        except Exception:
            pdf_error_placeholder.error("⚠️ Could not process PDF. Please upload the **actual Paytm UPI monthly statement PDF**.")
    
    elif form_submit:
        # Collect form expenses
        categories = {
            "Housing": housing,
            "Food & Groceries": food,
            "Transportation": transportation,
            "Utilities & Bills": utilities,
            "Entertainment": entertainment,
            "Healthcare": healthcare,
            "Shopping & Lifestyle": shopping,
            "Education": education,
            "Savings/Investments": savings,
            "Miscellaneous": misc
        }
        total_expense = sum(categories.values())
        percentages = {cat: round((amt / total_expense * 100), 2) if total_expense > 0 else 0
                       for cat, amt in categories.items()}
        data = {
            "timeframe": f"{start_date} to {end_date}",
            "total_expense": total_expense,
            "categories": categories,
            "percentages": percentages
        }
        st.session_state["chart_data"] = data
        # Build expense summary string
        expense_str = f"""
        Timeframe: {data['timeframe']}
        Monthly Income: {income}
        Savings Goal: {savings_goal}
        Debt/EMI: {debt}
        Total Expense: ₹{data['total_expense']}

        Categories & Amounts:
        """
        for cat, amt in data['categories'].items():
            pct = data['percentages'][cat]
            expense_str += f"{cat}: ₹{amt} ({pct}%)\n"
        st.session_state["expense_summary_payload"] = expense_str

# ---------- RIGHT COLUMN: Charts + Expense Summary ----------
with right_col:
    st.subheader("📊 Charts / 💬 Chatbot", divider="gray")
    st.markdown("<p style='text-align:center; font-size:18px; margin:5px;'>| Charts and Chatbot will appear here based on input from the left column |</p>", unsafe_allow_html=True)

    if "chart_data" in st.session_state:
        data = st.session_state["chart_data"]

            
        # Prepare data
        df = pd.DataFrame({
            "Category": list(data["categories"].keys()),
            "Amount (₹)": list(data["categories"].values())
        })
        df["Percentage"] = (df["Amount (₹)"] / data["total_expense"] * 100).round(2)
        df["Label"] = df["Percentage"].astype(str) + "%"

        # ---------- Altair chart ----------
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(
                'Category:N',
                sort=None,
                title='Expense Category',
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontWeight='bold',     # x-axis labels bold
                    titleFontWeight='bold'      # x-axis title bold
                )
            ),
            y=alt.Y(
                'Amount (₹):Q',
                title='Total Spent',
                axis=alt.Axis(
                    labelFontWeight='bold',     # y-axis labels bold
                    titleFontWeight='bold'      # y-axis title bold
                )
            ),
            color=alt.Color(
                'Category:N',
                legend=None   
            )
        ).properties(
            width="container",
            height=400
        )

        text = chart.mark_text(
            dy=-10,  # slightly above bar
            fontSize=15,
            fontWeight='bold',
            color='black'
        ).encode(
            text='Label'
        )

        st.subheader("Expense Distribution (₹ + %)")
        st.altair_chart(chart + text, use_container_width=True)

        # ---------- Donut chart ----------
        threshold = 0.05 * data['total_expense']
        small_cats = df[df["Amount (₹)"] < threshold]
        others_sum = small_cats["Amount (₹)"].sum()
        df_donut = df[df["Amount (₹)"] >= threshold].copy()
        if others_sum > 0:
            df_donut = pd.concat([df_donut, pd.DataFrame([{"Category":"Others","Amount (₹)":others_sum}])])
            
        # Plot donut chart with dark background
        fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0e1117")  # Streamlit dark theme background

        # Pie chart
        wedges, texts, autotexts = ax.pie(
            df_donut["Amount (₹)"],
            labels=df_donut["Category"],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
            labeldistance=1.1,
            explode=[0.05 if amt > df_donut["Amount (₹)"].mean() else 0 for amt in df_donut["Amount (₹)"]],
            shadow=False
        )
            
        plt.setp(texts, size=8)

        # Center circle with dark grey (to blend better)
        centre_circle = plt.Circle((0, 0), 0.70, fc="#0e1117")  
        fig.gca().add_artist(centre_circle)

        # Set axis background also dark
        ax.set_facecolor("#0e1117")
        ax.axis('equal')

        # Improve text color (white for contrast)
        plt.setp(autotexts, size=8, weight="bold", color="white")
        for t in texts:
            t.set_color("white")

        st.subheader("Category-wise Share (%)")
        st.pyplot(fig)
            

st.markdown(
    """
    <hr style="border: 2px solid #555; border-radius: 5px; margin-top: 20px; margin-bottom: 20px;">
    """,
    unsafe_allow_html=True
)

# ----- 2️⃣ Expense summary below the columns (CENTERED) -----
if "expense_summary_payload" in st.session_state:

    # Only call summarize API if it hasn't been generated yet
    if "summary_generated" not in st.session_state:
        st.write("")  # some spacing

        # 🌟 Wrap summary + chatbot inside a centered container with max-width
        st.markdown(
            """
            <div style="max-width: 800px; margin: 0 auto;">
            """,
            unsafe_allow_html=True
        )

        st.markdown("<h2 style='text-align: center;'>📊 Expense Summary</h2>", unsafe_allow_html=True)

        # Create placeholder for temporary message
        status_placeholder = st.empty()
        status_placeholder.info("📝 Generating summary... Please wait.")

        payload = {"expenses": st.session_state["expense_summary_payload"]}

        try:
            response = requests.post("http://127.0.0.1:8000/summarize", json=payload)

            # Once response is back, clear the placeholder
            status_placeholder.empty()

            if response.status_code == 200:
                st.session_state["summary"] = response.json()["summary"]
                # st.markdown(summary, unsafe_allow_html=True)
                st.session_state["summary_generated"] = True
            else:
                st.error(f"❌ Failed to get summary from backend. Status: {response.status_code}, Details: {response.text}")

        except Exception as e:
            status_placeholder.empty()
            st.error(f"⚠️ Error while generating summary: {e}")
        
    if "summary_generated" in st.session_state and st.session_state["summary_generated"]:
        st.markdown(st.session_state["summary"], unsafe_allow_html=True)

    # ------------CHATBOT----------------
    # ✅ Show chatbot ONLY after summary has been generated
    if "summary_generated" in st.session_state and st.session_state["summary_generated"]:
        st.markdown("<hr style='border: 2px solid #555; border-radius: 5px; margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>💬 Expense Chatbot</h2>", unsafe_allow_html=True)

        # Initialize session state for messages if not already
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        # Chat input appears only now
        query = st.chat_input("Ask me any query regarding your expenses...")

        if query:
            # Add user message
            st.session_state["messages"].append({"role": "user", "content": query})

            # Call FastAPI backend for chatbot response
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={
                    "query": query,
                    "expenses": st.session_state["expense_summary_payload"]
                }
            )
            bot_reply = response.json().get("answer", "⚠️ Something went wrong.")

            # Add bot reply
            st.session_state["messages"].append({"role": "bot", "content": bot_reply})

        # Display message history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 🧹 Close the centered div container
    st.markdown("</div>", unsafe_allow_html=True)

