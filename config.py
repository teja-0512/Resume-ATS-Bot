import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
# Telegram Configuration
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
    raise ValueError(
        "BOT_TOKEN is not set or is a placeholder. "
        "Add a valid token to the .env file."
    )

# ==============================
# OpenAI Configuration
# ==============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
    OPENAI_API_KEY = None

# ==============================
# Project Directories
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ==============================
# Resume Configuration
# ==============================
SUPPORTED_FORMATS = [".pdf", ".docx"]

MAX_FILE_SIZE_MB = 10

# ==============================
# AI Model
# ==============================
OPENAI_MODEL = "gpt-5.5"

# ==============================
# ATS Scoring Weights
# ==============================
ATS_WEIGHTS = {
    "Contact Information": 5,
    "Professional Summary": 10,
    "Skills": 20,
    "Projects": 20,
    "Experience": 20,
    "Education": 10,
    "Certifications": 5,
    "Formatting": 5,
    "Grammar": 5,
}