import json
import re
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from clients import OPENAI_API  
from openai import OpenAI
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Read the OpenAI API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("The OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)
logger.info("OpenAI client initialized")

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
    """
    Remove ineffective HTML tags from the given HTML string,
    remove unwanted invisible characters, and preserve block structure.
    """
    logger.debug("Starting HTML cleaning")
    soup = BeautifulSoup(html_str, 'html.parser')
    for tag in soup(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()
    raw_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    text = "\n".join(lines)
    cleaned_text = re.sub(r"[\u00ad\u034f\u200c\u200d]+", "", text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    logger.debug("HTML cleaning completed")
    return cleaned_text

def extract_subscription_info(email_json: str) -> EmailSubscriptionExtraction:
    """
    Extracts structured subscription information from an email represented as a JSON string.
    The email JSON is expected to contain keys: 'subject', 'body', 'snippet', and 'from'.
    """
    logger.info("Starting subscription info extraction")
    try:
        email_data = json.loads(email_json)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
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
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=EmailSubscriptionExtraction,
        )
        logger.info("Successfully extracted subscription information")
        return completion.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {e}")
        return None

def process_emails_from_list(emails: list) -> list:
    """
    For each email in the list, clean the HTML in 'body', compute its length,
    and extract subscription info using GPT.
    """
    logger.info(f"Processing {len(emails)} emails")
    processed = []
    for i, email in enumerate(emails):
        logger.debug(f"Processing email {i+1}/{len(emails)}")
        if "body" in email:
            original_body = email["body"]
            cleaned_body = clean_html(original_body)
            email["body"] = cleaned_body
            email["body_length"] = len(cleaned_body)
        email_json_str = json.dumps(email)
        subscription_info = extract_subscription_info(email_json_str)
        email["subscription_info"] = subscription_info.model_dump() if subscription_info else None
        processed.append(email)
    logger.info("Email processing completed")
    return processed

def ensure_output_directory():
    """Ensure the output directory exists"""
    global output_directory
    try:
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating output directory: {e}")
        return False

from config_util import get_output_directory

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

def save_json_file(data: dict, filename: str) -> str:
    global output_directory
    # Refresh the output_directory value from config
    output_directory = get_output_directory()
    
    if not ensure_output_directory():
        raise Exception("Output directory is not available.")
    
    # If output_directory is relative, make it relative to backend directory
    if not os.path.isabs(output_directory):
        output_directory = os.path.join(BACKEND_DIR, output_directory)
    
    # Ensure the output directory is 'output'
    output_directory = os.path.join(BACKEND_DIR, 'output')

    filepath = os.path.join(output_directory, filename)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"File saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving file {filepath}: {e}")
        raise

def compute_analytics(processed_emails: list) -> dict:
    """
    Computes detailed analytics including success/failure rates, category distributions,
    subscription amounts by service, duplicate subscriptions and deduplicated subscriptions.
    Deduplicated subscriptions are grouped by the subscription name.
    """
    logger.info("Computing analytics")
    total_emails = len(processed_emails)
    successful_extractions = [email for email in processed_emails if email.get("subscription_info")]
    failed_extractions = [email for email in processed_emails if not email.get("subscription_info")]
    
    # Category and service analytics
    category_distribution = {}
    service_amounts = {}
    subscription_occurrences = {}  # Track subscription occurrences
    
    # Group subscriptions by name for deduplication.
    deduplicated_subscriptions = {}
    
    for email in successful_extractions:
        sub_info = email["subscription_info"]
        if sub_info:
            # Update category distribution.
            category = sub_info.get("category", "unknown")
            category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Update service amounts and track occurrences.
            name = sub_info.get("name")
            amount = sub_info.get("amount")
            if name:
                # Count occurrences.
                subscription_occurrences[name] = subscription_occurrences.get(name, 0) + 1

                # For deduplication, group by subscription name.
                if name not in deduplicated_subscriptions:
                    deduplicated_subscriptions[name] = {
                        "subscription_info": sub_info,
                        "count": 1
                    }
                else:
                    deduplicated_subscriptions[name]["count"] += 1

                # Service amounts computation.
                if amount:
                    if name not in service_amounts:
                        service_amounts[name] = {"total": 0, "count": 0}
                    service_amounts[name]["total"] += amount
                    service_amounts[name]["count"] += 1

    # Calculate average amounts per service.
    service_analytics = {
        name: {
            "average_amount": info["total"] / info["count"],
            "subscription_count": info["count"]
        }
        for name, info in service_amounts.items()
    }
    
    # Calculate duplicate subscriptions (only those with more than one occurrence).
    duplicate_subscriptions = {
        name: count for name, count in subscription_occurrences.items() if count > 1
    }
    
    duplicate_subscriptions_details = {}
    for email in successful_extractions:
        sub_info = email["subscription_info"]
        if sub_info:
            name = sub_info.get("name")
            if name in duplicate_subscriptions:
                if name not in duplicate_subscriptions_details:
                    duplicate_subscriptions_details[name] = {
                        "count": subscription_occurrences[name],
                        "emails": []
                    }
                duplicate_subscriptions_details[name]["emails"].append({
                    "subject": email.get("subject"),
                    "body_length": email.get("body_length"),
                    "category": sub_info.get("category")
                })
    
    analytics = {
        "total_emails": total_emails,
        "successful_extractions": len(successful_extractions),
        "failed_extractions": len(failed_extractions),
        "category_distribution": category_distribution,
        "service_analytics": service_analytics,
        "duplicate_subscriptions": {
            "total_duplicates": len(duplicate_subscriptions),
            "details": duplicate_subscriptions
        },
        "duplicate_subscriptions_details": duplicate_subscriptions_details,
        "deduplicated_subscriptions": deduplicated_subscriptions  # New grouping information.
    }
    
    # Save analytics to JSON file.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"analytics_{timestamp}.json"
    
    try:
        filepath = save_json_file(analytics, output_filename)
        logger.info(f"Analytics saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving analytics to file: {e}")
    
    logger.info(f"Analytics computed: {analytics}")
    return analytics

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized with CORS")

# In-memory storage for processed emails
processed_emails_storage = []

output_directory = os.path.join(os.getcwd(), "output")  # Default output directory

from config_util import set_output_directory_config

@app.post("/set-output-directory")
async def set_output_directory(directory: dict):
    path = directory.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Directory path is required")
    
    try:
        # This will validate, normalize and set the new directory
        new_dir = set_output_directory_config(path)
        
        global output_directory
        output_directory = new_dir
        logger.info(f"Output directory set to: {output_directory}")
        return {
            "status": "success", 
            "directory": output_directory,
            "absolutePath": os.path.abspath(output_directory),
            "exists": os.path.exists(output_directory),
            "isWriteable": os.access(output_directory, os.W_OK)
        }
    except ValueError as e:
        logger.error(f"Invalid directory: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting output directory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set output directory: {str(e)}")

@app.get("/current-directory")
async def get_current_directory():
    """Get the current output directory configuration"""
    try:
        current_dir = get_output_directory()
        abs_path = os.path.abspath(current_dir)
        return {
            "directory": current_dir,
            "absolutePath": abs_path,
            "exists": os.path.exists(abs_path),
            "isWriteable": os.access(abs_path, os.W_OK)
        }
    except Exception as e:
        logger.error(f"Error getting current directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify-directory/{path:path}")
async def verify_directory(path: str):
    """Verify if a directory path is valid and writable"""
    try:
        is_valid, error = validate_directory(path)
        abs_path = os.path.abspath(path)
        return {
            "isValid": is_valid,
            "error": error if not is_valid else "",
            "absolutePath": abs_path,
            "exists": os.path.exists(abs_path),
            "isWriteable": os.access(abs_path, os.W_OK) if os.path.exists(abs_path) else False
        }
    except Exception as e:
        logger.error(f"Error verifying directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-emails")
async def process_emails_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to process a JSON file containing email objects.
    Returns a list of processed emails with cleaned bodies and extracted subscription info.
    Also saves results to a JSON file.
    """
    logger.info(f"Received file upload: {file.filename}")
    try:
        content = await file.read()
        emails = json.loads(content)
        logger.info(f"Successfully parsed JSON with {len(emails)} emails")
        if not isinstance(emails, list):
            logger.error("Invalid JSON format: expected a list of emails")
            raise HTTPException(status_code=400, detail="Invalid JSON format: expected a list of emails")
        
        processed = process_emails_from_list(emails)
        global processed_emails_storage
        processed_emails_storage = processed
        
        # Save processed results to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"processed_emails_{timestamp}.json"
        saved_filepath = None
        
        try:
            saved_filepath = save_json_file(processed, output_filename)
            logger.info(f"Results saved to {saved_filepath}")
        except Exception as e:
            logger.error(f"Error saving results to file: {e}")
            # Continue execution even if file save fails
        
        return JSONResponse(content={
            "status": "success", 
            "data": processed,
            "savedPath": saved_filepath
        })
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def analytics_endpoint():
    """
    Endpoint to return analytics computed on processed emails.
    Uses in-memory storage instead of file storage.
    """
    logger.info("Analytics endpoint called")
    try:
        analytics = compute_analytics(processed_emails_storage)
        return JSONResponse(content=analytics)
    except Exception as e:
        logger.error(f"Error computing analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error computing analytics")

# Ensure output directory exists at startup
output_directory = os.path.join(BACKEND_DIR, "output")  # Default output directory relative to backend
ensure_output_directory()
logger.info(f"Output directory initialized at: {output_directory}")

if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)