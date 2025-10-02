from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.chatbot import summarize_user_expenses
import uvicorn

app = FastAPI()

# allow all origins for now (safe for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body
class ExpenseRequest(BaseModel):
    expenses: str

@app.get("/")
async def root():
    return {"message": "Backend is running!"}

@app.post("/summarize")
async def summarize_expenses(req: ExpenseRequest):
    try:
        summary = summarize_user_expenses(req.expenses)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
