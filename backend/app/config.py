import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret")

# Gmail scopes: read + send + modify (modify needed for read/unread toggling)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

# NOTE (trade-off, documented in README): this is a single-user demo app.
# OAuth tokens are persisted to a local JSON file rather than a per-user
# database/session store. Good enough for a hiring-task demo; the first
# thing to fix for multi-user production use is per-session token storage.
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "token.json")
