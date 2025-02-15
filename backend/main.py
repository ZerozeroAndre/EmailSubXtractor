# backend/main.py
import json
import re
from io import BytesIO
from bs4 import BeautifulSoup
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

class EmailSubscriptionExtraction(BaseModel):
    name: str      # Subscription name or service provider
    amount: float  # Subscription cost if available
    cycle: str     # Expected values: monthly, yearly, weekly, bi-weekly, quarterly, bi-monthly, bi-yearly, or unknown    
    start_date: str  # Date the subscription starts
    is_trial: bool   # Whether the subscription is a trial
    trial_duration_in_days: int  # Duration of the trial in days
    trial_end_date: str
    category: str

def clean_html(html_str: str) -> str:
    soup = BeautifulSoup(html_str, 'html.parser')
    for tag in soup(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()
    raw_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    text = "\n".join(lines)
    cleaned_text = re.sub(r"[\u00ad\u034f\u200c\u200d]+", "", text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    return cleaned_text

def extract_subscription_info(email_json: str) -> EmailSubscriptionExtraction:
    try:
        email_data = json.loads(email_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    combined_text = (
        f"Subject: {email_data.get('subject', '')}\n"
        f"Body: {email_data.get('body', '')}\n"
        f"Snippet: {email_data.get('snippet', '')}\n"
        f"From: {email_data.get('from', '')}"
    )
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert at structured data extraction. You will be given an email in the following JSON structure:\n\n"
                "{\n"
                '  "subject": "string",  // Subject line of the email\n'
                '  "body": "string",     // Full email body\n'
                '  "snippet": "string",  // Short preview of the email content\n'
                '  "from": "string"      // Sender\'s email address\n'
                "}\n\n"
                "Your task is to extract the following structured subscription information:\n\n"
                "name: 'string'                          // Subscription name or service provider\n"
                "amount: 'number (optional)'             // Subscription cost if available\n"
                "cycle: 'string'                         // Expected values: monthly, yearly, weekly, bi-weekly, quarterly, bi-monthly, bi-yearly, or unknown\n"
                "start_date: 'date'                       // Date the subscription starts\n"
                "is_trial: 'boolean (optional)'\n"
                "trial_duration_in_days: 'number (optional)' // Duration of the trial in days\n"
                "trial_end_date: 'string (optional)'      // End date of the trial, if applicable\n"
                "category: 'string'                       // e.g., insurances, utility, rent, etc."
            )
        },
        {
            "role": "user",
            "content": combined_text,
        }
    ]
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=messages,
        response_format=EmailSubscriptionExtraction,
    )
    
    return completion.choices[0].message.parsed

def process_emails_from_list(emails: list) -> list:
    processed = []
    for email in emails:
        if "body" in email:
            original_body = email["body"]
            cleaned_body = clean_html(original_body)
            email["body"] = cleaned_body
            email["body_length"] = len(cleaned_body)
        email_json_str = json.dumps(email)
        subscription_info = extract_subscription_info(email_json_str)
        email["subscription_info"] = subscription_info.model_dump() if subscription_info else None
        processed.append(email)
    return processed

def compute_analytics(processed_emails: list) -> dict:
    total_emails = len(processed_emails)
    total_length = sum(email.get("body_length", 0) for email in processed_emails)
    avg_length = total_length / total_emails if total_emails > 0 else 0

    # Example: Count emails with extracted subscription info
    subscription_count = sum(1 for email in processed_emails if email.get("subscription_info") is not None)
    
    return {
        "total_emails": total_emails,
        "average_body_length": avg_length,
        "subscription_count": subscription_count
    }

app = FastAPI()

@app.post("/process-emails")
async def process_emails_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    emails = json.loads(content)
    processed = process_emails_from_list(emails)
    return JSONResponse(content=processed)

@app.get("/analytics")
async def analytics_endpoint():
    # In a real-world scenario, you might store the processed data or compute analytics on demand.
    # For demo purposes, we assume a file is processed and analytics are computed.
    file_path = "path/to/processed_emails.json"
    with open(file_path, "r", encoding="utf-8") as f:
        processed = json.load(f)
    analytics = compute_analytics(processed)
    return JSONResponse(content=analytics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)