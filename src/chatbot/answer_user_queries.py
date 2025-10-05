from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.memory import ConversationSummaryMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.constants import CHAT_MODEL, CONVERSATION_SUMMARIZER_MODEL
from dotenv import load_dotenv
import os 

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

#Initialize llama-3.3-70b-versatile
groq_llm = ChatGroq(
        model=CONVERSATION_SUMMARIZER_MODEL,  
        temperature=0,
        api_key=api_key,
        timeout=60,
        max_retries=2
    )

# Initialize Gemini 2.5 Pro
gemini_llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL,
    temperature=0,          
    max_output_tokens=65535    
)

# Conversation summary memory
memory = ConversationSummaryMemory(
    llm=groq_llm,
    memory_key="chat_history",
    return_messages=True
)

parser = StrOutputParser()

template="""
You are a highly intelligent and financially savvy assistant that helps users analyze their personal expenses.

You have access to:
1. **Actual Expenses Data** (calculated programmatically):  
{actual_expenses}

2. **Relevant Extracts from a Previously Generated Detailed Expense Summary**:  
{retrieved_context}

3. A **summary of the conversation so far**, which helps you maintain context and avoid repetition:
{conversation_summary}

The user asked:
"{user_query}"

Using the above information, give a **clear, accurate, and contextual answer** to the user's query. 
- If the question can be answered using the expense data or retrieved summary, do so directly.
- If the question is follow-up or ambiguous, rely on conversation summary for context.
- Be concise but insightful. If calculations are needed, show them clearly.
"""

prompt = PromptTemplate(
    template=template,
    input_variables=['user_query', 'actual_expenses', 'retrieved_context', 'conversation_summary']
)

def answer_user_queries(user_query: str, actual_expenses: str, retrieved_context: str) -> str:
    """
    Takes in a user query and answers it accurately using:
    - Actual expense data (passed in)
    - Top relevant chunks from expense summary (passed in)
    - Summarized conversation history
    - Gemini LLM for final response
    """
    #Load the conversation summary
    conversation_summary = memory.load_memory_variables({}).get("chat_history", "")

    chain = prompt | gemini_llm | parser

    response = chain.invoke({
        'actual_expenses': actual_expenses,
        'retrieved_context': retrieved_context,
        'conversation_summary': conversation_summary,
        'user_query': user_query
    })
    
    # Save conversation turn
    memory.save_context({"query": user_query}, {"response": response})

    return response 