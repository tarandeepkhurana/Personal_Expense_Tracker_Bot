from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from src.constants import UPLOAD_DIR
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.chatbot.summarize_user_expenses import (summarize_user_expenses, 
  fetch_relevant_summary_chunks, store_summary_in_chroma)
from src.paytm_pdf_parser.parse_pdf import parse_paytm_pdf
from src.chatbot.answer_user_queries import answer_user_queries
from src.constants import NUM_DOCS_TO_FETCH
import uvicorn
import os

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

class QueryRequest(BaseModel):
    query: str 
    expenses: str

@app.get("/")
async def root():
    return {"message": "Backend is running!"}

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)  #Create a file path

        #Save the uploaded file
        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)

        result_json = parse_paytm_pdf(str(file_path))

        return JSONResponse(content=result_json)
    except Exception as e:
        return {'error': str(e)}

@app.post("/summarize")
async def summarize_expenses(req: ExpenseRequest):
    try:
        summary = summarize_user_expenses(req.expenses)
        store_summary_in_chroma(summary)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        user_query = request.query
        actual_expenses = request.expenses
        retrieved_context = fetch_relevant_summary_chunks(user_query, NUM_DOCS_TO_FETCH)
        
        response = answer_user_queries(user_query, actual_expenses, retrieved_context)
        return {'answer': response}
    except Exception as e:
        return {'error': str(e)}
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
