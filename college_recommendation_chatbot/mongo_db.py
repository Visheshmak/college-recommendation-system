from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)

db = client["college_recommendation"]

students_col = db["students"]
intents_col = db["intents"]
colleges_col = db["colleges"]  # Collection for college cutoffs
college_details_col = db["college_details"]  # NEW: Collection for detailed college info
search_logs_col = db["search_logs"]  # Logs for user search queries
users_col = db["users"]  # Collection for user accounts
saved_colleges_col = db["saved_colleges"]  # Collection for saved/bookmarked colleges
reviews_col = db["reviews"]  # Collection for college reviews

# Email Configuration
MAIL_CONFIG = {
    "MAIL_SERVER": os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    "MAIL_PORT": int(os.getenv("MAIL_PORT", 587)),
    "MAIL_USE_TLS": os.getenv("MAIL_USE_TLS", True),
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD", "your-app-password"),
    "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER", "college-recommendation@example.com")
}

