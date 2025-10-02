# 💰 Personal Expense Tracker Bot

A smart financial assistant that helps you track your expenses, analyze spending habits, and get personalized recommendations to improve your finances. Built with **Streamlit** frontend, **FastAPI** backend, and powered by **LangChain + Google Gemini 2.5 Pro** LLM.

---

## Features

- Input your expenses across multiple categories for any timeframe.
- Supports specifying **monthly income, savings goal, and debt/EMI**.
- Generates a **detailed analysis**, including:
  - Concise summary of spending habits
  - Biggest expense categories (with % of income)
  - Essentials vs Non-Essentials split
  - Savings goal tracking
  - Red flags and overspending areas
  - Personalized recommendations
- Multi-month expense analysis using monthly income reference.
- Dockerized for local development and easy deployment.

---

## Deployment
- Backend and frontend are separately dockerized, ready for deployment on platforms like Render.
- Make sure to set the GOOGLE_API_KEY environment variable on the deployed platform.
- Frontend requests the deployed backend URL (replace the public backend URL with yours in the streamlit_app.py).
