from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_chroma import Chroma
from src.constants import EMBEDDING_MODEL, EXPENSE_SUMMARIZER_MODEL
from dotenv import load_dotenv
import os 
import re 
import uuid

load_dotenv()

#Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

#Initialize vector store
vector_store = Chroma(
    collection_name="expense_summary_collection",
    embedding_function=embeddings,
)

def summarize_user_expenses(user_expenses: str) -> str:
    """
    Takes user expenses as an input and summarizes it
    using llm.
    """
    # Initialize Gemini 2.5 Pro
    llm = ChatGoogleGenerativeAI(
        model=EXPENSE_SUMMARIZER_MODEL,
        temperature=0,          
        max_output_tokens=65535    
    )

    template="""
    You are a financial advisor. Here is a user’s financial record:

    {user_expenses}
    
    Note: The expenses listed above are **for the entire timeframe** specified, which may span multiple months. Use the provided monthly income to compute percentages and evaluate spending patterns **on a per-month basis**.

    Please analyze this and provide:
    1. A concise summary of spending habits  
    2. Biggest 2–3 expense categories (with % of income)  
    3. Spending split: Essentials vs Non-Essentials  
    4. How the user did against their savings goal  
    5. Red flags (overspending areas, debt risk, imbalance)  
    6. 2–3 personalized recommendations to improve finances
    """

    parser = StrOutputParser()

    prompt = PromptTemplate(
        template=template,
        input_variables=["user_expenses"]
    )

    chain = prompt | llm | parser 

    result = chain.invoke({
        'user_expenses': user_expenses
    })

    return result

import re

def chunk_summary(summary_text: str) -> list[dict]:
    """
    Splits the financial summary into 6 well-defined numbered chunks.
    Ignores any intro text before point 1.
    Returns a list of dicts like:
    [{'title': '1. Concise Summary of Spending Habits', 'text': '...'}, ...]
    """
    # Regex to match each numbered section from 1. to 6.
    pattern = r"^\s*(\d\..*?)(?=(?:^\s*\d\.|\Z))"
    matches = re.findall(pattern, summary_text, flags=re.DOTALL | re.MULTILINE)

    chunks = []
    for i, section in enumerate(matches, start=1):
        # The title is usually the first line (e.g., "1. Concise Summary of Spending Habits")
        lines = section.strip().splitlines()
        title = lines[0].strip()
        text = "\n".join(lines[1:]).strip()

        chunks.append({
            "title": title,
            "text": text
        })

    return chunks


def store_summary_in_chroma(summary_text: str) -> None:
    """
    Store the 6-point expense summary into Chroma for retrieval.
    """
    try:
        # Split summary
        chunks = chunk_summary(summary_text)

        existing_ids = vector_store.get()["ids"]
        if existing_ids:  
            vector_store.delete(ids=existing_ids)
        
        # Prepare documents
        docs = []
        for chunk in chunks:
            docs.append(Document(
                id=str(uuid.uuid4()),          # unique ID for each chunk
                page_content=chunk['title'] + chunk["text"],   
                metadata={"title": chunk["title"]}
            ))
        
        # Add to vector store
        vector_store.add_documents(docs)
        print("Chunks added in chroma.")
    except Exception as e:
        print(e)

    
def fetch_relevant_summary_chunks(user_query: str, k: int) -> str:
    """
    Retrieve the most relevant expense summary chunks for a given query.
    """
    results = vector_store.similarity_search(query=user_query, k=k)
    context = " ".join([doc.page_content for doc in results])
    return context

if __name__ == "__main__":

    summary = """
    Of course. As a financial advisor, here is a detailed analysis of your financial record for May 2025.
Hello, thank you for sharing your financial data. My analysis is designed to provide a clear picture of your financial health and offer actionable steps for improvement. The most critical factor in this period is that your expenses were funded entirely without a formal monthly income, likely from savings or another source.

Here is your financial breakdown:

1. Concise Summary of Spending Habits
During May, your spending totaled ₹4,329.18 against a reported income of ₹0. This indicates a complete reliance on other funds to cover expenses. Your spending is heavily concentrated on essential needs, with Food and Bills alone making up over 67% of your total outflow. Discretionary spending, such as on Shopping, was minimal, which shows good control over non-essential purchases.

2. Biggest Expense Categories
Calculating expenses as a percentage of income isn't possible as your income was ₹0. Instead, here are your largest expense categories as a percentage of your total spending:

Food: ₹2,002.21 (46.25% of total spending)
Bills: ₹939.82 (21.71% of total spending)
Travel: ₹407.15 (9.40% of total spending)
These three categories represent nearly 78% of your entire budget for the month.

3. Spending Split: Essentials vs. Non-Essentials
To understand your priorities, I've categorized your spending.

Essential Spending: ₹4,152.18 (95.9%)
This includes Food, Bills, Groceries, Fuel, and Travel (assuming it's for necessary commutes).
Non-Essential Spending (Wants): ₹90.0 (2.1%)
This includes Shopping.
Needs Context: ₹387.0 (8.9%)
Transfers could be essential (like rent or supporting family) or non-essential. Without more detail, it remains uncategorized.
Analysis: Your budget is extremely lean, with over 95% of your known expenses dedicated to absolute necessities. This is a responsible approach when funds are limited.

4. How You Did Against Your Savings Goal
Your savings goal was ₹0. With an income of ₹0 and expenses of ₹4,329.18, you had a net deficit of -₹4,329.18. This means you did not meet your savings goal; instead, you had to draw down on existing funds by this amount to cover your costs.

5. Red Flags
Major Income/Expense Imbalance: The most significant red flag is spending money without any reported income. This is an unsustainable financial situation that can rapidly deplete savings or lead to debt.
High Concentration in Food Spending: While essential, having nearly half of your total spending go towards food is very high. This category may contain a mix of cost-effective groceries and more expensive dining out or takeaways, presenting an opportunity for optimization.
Risk of Depleting Savings: Continuously funding living expenses from savings without replenishing them is a high-risk strategy. This leaves you vulnerable to emergencies and depletes your long-term financial safety net.
6. Personalized Recommendations
Your immediate priority must be to address the income-expense gap. Here are three actionable steps:

Prioritize Establishing an Income Stream: Your most urgent task is to secure a source of income, whether it's through full-time employment, part-time work, or freelance opportunities. All other financial goals are secondary until you have a positive cash flow.
Scrutinize Your Food Budget: Since food is your largest expense, focus your efforts here. Break down the "Food" category into "Groceries" vs. "Dining Out/Takeaway." Challenge yourself to reduce this cost by 15-20% through meal planning, cooking at home, buying in bulk, and avoiding impulse food purchases. This is the quickest way to reduce your monthly cash burn.
Build a "Bare-Bones" Budget: Create a minimum-survival budget that includes only absolute essentials (rent, basic groceries, utilities). Your current spending is already close to this, but formalizing it will give you a clear target to cover as soon as you start earning. Once income is stable, your first goal should be to build an emergency fund covering 3-6 months of these essential expenses.
Your spending habits show discipline in avoiding non-essentials. The fundamental issue is on the income side. By focusing on generating income and optimizing your largest expense category, you can quickly move towards a more stable financial future.
    """
    store_summary_in_chroma(summary)
    print(fetch_relevant_summary_chunks("Can you elaborate the Bare-Bones budget you are talking about", 2))