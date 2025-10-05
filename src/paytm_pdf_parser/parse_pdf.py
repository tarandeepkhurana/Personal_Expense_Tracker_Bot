import re
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader

def parse_paytm_pdf(pdf_path: str) -> dict:
    """
    Parse a Paytm UPI statement PDF and extract transaction and user information.
    
    This function reads a Paytm UPI statement PDF, extracts user details, transaction
    summary, and individual transaction records, then categorizes and aggregates the
    spending data.
    
    Args:
        pdf_path (str): Path to the Paytm UPI statement PDF file.
    
    Returns:
        dict: A dictionary containing:
            - name (str): User's full name
            - phone (str): User's phone number (10 digits)
            - email (str): User's email address
            - timeframe (str): Statement period (e.g., "1 MAY'25 - 31 MAY'25")
            - total_money_paid (float): Total amount paid during the period
            - total_money_received (float): Total amount received during the period
            - total_expense (float): Sum of all transaction amounts
            - categories (dict): Spending breakdown by category with amounts
            - percentages (dict): Percentage distribution of spending by category
            - transaction_count (int): Total number of transactions parsed
    """
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    full_text = "\n".join([doc.page_content for doc in docs])

    # ----- Extract user info from the first page -----
    first_page_text = docs[0].page_content

    # Extract name - it's between "Contact Us" and the phone number line
    name_pattern = re.compile(r"Contact Us\s*\n\s*([A-Z][A-Z\s]+?)\s*\n\s*(\d{10})", re.MULTILINE)
    name_match = name_pattern.search(first_page_text)
    
    if name_match:
        name = name_match.group(1).strip()
        phone = name_match.group(2).strip()
    else:
        name = ""
        phone = ""
    
    # Extract email
    email_pattern = re.compile(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")
    email_match = email_pattern.search(first_page_text)
    email = email_match.group(1) if email_match else ""

    # Timeframe
    timeframe_pattern = re.compile(r"UPI Statement for\s*\n\s*(.*?)(?:\n|$)")
    timeframe_m = timeframe_pattern.search(first_page_text)
    timeframe = timeframe_m.group(1).strip() if timeframe_m else ""

    # Total Money Paid
    total_paid_pattern = re.compile(r"Total Money Paid\s*-\s*Rs\.?([\d,]+(?:\.\d{1,2})?)")
    total_paid_m = total_paid_pattern.search(first_page_text)
    total_paid = float(total_paid_m.group(1).replace(",", "")) if total_paid_m else None

    # Total Money Received
    total_received_pattern = re.compile(r"Total Money Received\s*\+\s*Rs\.?([\d,]+(?:\.\d{1,2})?)")
    total_received_m = total_received_pattern.search(first_page_text)
    total_received = float(total_received_m.group(1).replace(",", "")) if total_received_m else None

    # ----- Extract transactions -----
    # Split by date pattern to get individual transactions
    transaction_blocks = re.split(r'(\d{1,2}\s+\w{3}\s+\d{1,2}:\d{2}\s+[AP]M)', full_text)
    
    transactions = []
    
    for i in range(1, len(transaction_blocks), 2):
        if i + 1 < len(transaction_blocks):
            date_time = transaction_blocks[i].strip()
            content = transaction_blocks[i + 1]
            
            # Extract date only
            date_match = re.match(r'(\d{1,2}\s+\w{3})', date_time)
            date = date_match.group(1) if date_match else ""
            
            # Extract merchant
            merchant_match = re.search(r'((?:Paid to|Money sent to)\s+[^\n]+)', content)
            merchant = merchant_match.group(1).strip() if merchant_match else ""
            
            # Extract amount
            amount_match = re.search(r'-\s*Rs\.?([\d,]+(?:\.\d{1,2})?)', content)
            amount = float(amount_match.group(1).replace(",", "")) if amount_match else None
            
            # Extract category/tag
            tag_match = re.search(r'Tag:\s*#\s*([^\n]+)', content)
            category = tag_match.group(1).strip() if tag_match else ""
            
            # Only add if we have essential info
            if date and merchant and amount and category:
                transactions.append({
                    "Date": date,
                    "Merchant": merchant,
                    "Amount": amount,
                    "Category": category
                })

    df = pd.DataFrame(transactions)
    
    # Normalize category names
    df["Category"] = df["Category"].replace({
        "Bill Payments": "Bills",
        "✈️ Travel": "Travel",
        "️ Fuel": "Fuel"
    })

    category_totals = df.groupby("Category")["Amount"].sum().to_dict()
    total_expense = sum(category_totals.values())
    percentages = {cat: round((amt/total_expense)*100, 2) for cat, amt in category_totals.items()}

    result = {
        "name": name,
        "phone": phone,
        "email": email,
        "timeframe": timeframe,
        "total_money_paid": total_paid,
        "total_money_received": total_received,
        "total_expense": round(total_expense, 2),
        "categories": {k: round(v, 2) for k, v in category_totals.items()},
        "percentages": percentages,
        "transaction_count": len(transactions)
    }

    return result

if __name__ == "__main__":
    result = parse_paytm_pdf("Paytm_UPI_Statement_May_2025.pdf")
    print(result)