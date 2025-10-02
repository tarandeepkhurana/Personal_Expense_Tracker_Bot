from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os 

load_dotenv()

def summarize_user_expenses(user_expenses: str) -> str:
    """
    Takes user expenses as an input and summarizes it
    using llm.
    """
    # Initialize Gemini 2.5 Pro
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
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

if __name__ == "__main__":
    exp="""
Timeframe: 2025-09-01 to 2025-09-30
Monthly Income: 40000
Savings Goal: 8000
Debt/EMI: 5000

Expenses:
Housing: 12000
Food & Groceries: 8500
Transportation: 3000
Utilities & Bills: 2200
Entertainment: 1500
Healthcare: 1000
Shopping & Lifestyle: 2500
Education: 2000
Savings/Investments: 5000
Other: 800

    """
    result = summarize_user_expenses(exp)
    print(result)