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

## Technologies Used

| Layer / Component       | Technology / Tool                 | Purpose / Description                                         |
|------------------------|----------------------------------|---------------------------------------------------------------|
| Frontend               | Streamlit                        | Web app UI to collect user input and display expense summary |
| Backend                | FastAPI                          | API server to handle requests and connect to the LLM         |
| Language Model         | Google Gemini 2.5 Pro via LangChain | Summarization and financial analysis of user expenses       |
| Prompt Management      | LangChain PromptTemplate         | Structure prompts for the LLM                                 |
| Output Parsing         | LangChain StrOutputParser        | Convert LLM output into usable text                           |
| Containerization       | Docker & Docker Compose          | Package backend and frontend into separate containers        |
| Deployment             | Render                           | Host and serve both backend and frontend                     |
| Environment Management | python-dotenv                    | Manage API keys and environment variables                    |
| Programming Language   | Python 3.12                      | Main development language                                     |
| HTTP Requests          | Requests library                  | Communicate between frontend and backend                     |
| Dependency Management  | pip / requirements.txt           | Install required Python packages                              |

---

## Deployment
- Backend and frontend are separately dockerized, ready for deployment on platforms like Render.
- Make sure to set the GOOGLE_API_KEY environment variable on the deployed platform.
- Frontend requests the deployed backend URL (replace the public backend URL with yours in the streamlit_app.py).
