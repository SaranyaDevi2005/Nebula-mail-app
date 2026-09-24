"""
Gmail OAuth flow.

Single-user demo design: after the user approves access once, we store the
resulting credentials in a local token.json file and reuse/refresh them on
every request. This avoids building session/user management for a 1-day
hiring task while keeping the OAuth flow itself fully real.
"""
import json
import os

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials

from . import config

router = APIRouter()


def _flow() -> Flow:
    client_config = {
        "web": {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [config.GOOGLE_REDIRECT_URI],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=config.GMAIL_SCOPES,
        redirect_uri=config.GOOGLE_REDIRECT_URI,
    )


def save_credentials(creds: Credentials) -> None:
    with open(config.TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def load_credentials() -> Credentials | None:
    if not os.path.exists(config.TOKEN_FILE):
        return None
    with open(config.TOKEN_FILE, "r") as f:
        data = json.load(f)
    creds = Credentials.from_authorized_user_info(data, config.GMAIL_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        save_credentials(creds)
    return creds


def is_authenticated() -> bool:
    creds = load_credentials()
    return creds is not None and creds.valid


@router.get("/auth/login")
def login():
    flow = _flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # forces refresh_token to be issued every time (fine for a demo)
    )
    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def callback(code: str):
    flow = _flow()
    flow.fetch_token(code=code)
    save_credentials(flow.credentials)
    return RedirectResponse(config.FRONTEND_URL)


@router.get("/auth/status")
def status():
    return {"authenticated": is_authenticated()}
