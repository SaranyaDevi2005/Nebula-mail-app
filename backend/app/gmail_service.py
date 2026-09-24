"""
Thin wrapper around the Gmail API: list, get, send, search.

Kept deliberately dumb/RESTful — both the UI and the assistant call the
exact same functions, so there's one source of truth for "what an email
looks like" and one place where Gmail query syntax is built.
"""
import base64
from email.mime.text import MIMEText
from typing import Optional

from googleapiclient.discovery import build

from .auth import load_credentials


def _service():
    creds = load_credentials()
    if creds is None:
        raise RuntimeError("Not authenticated. Visit /auth/login first.")
    return build("gmail", "v1", credentials=creds)


def _header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _extract_body(payload: dict) -> str:
    """Walk the MIME tree and return the first text/plain (fallback text/html) part."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    if "parts" in payload:
        # prefer text/plain among children
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload["parts"]:
            nested = _extract_body(part)
            if nested:
                return nested

    if "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    return ""


def _parse_message(msg: dict, full: bool = False) -> dict:
    headers = msg.get("payload", {}).get("headers", [])
    parsed = {
        "id": msg["id"],
        "threadId": msg.get("threadId"),
        "sender": _header(headers, "From"),
        "to": _header(headers, "To"),
        "subject": _header(headers, "Subject") or "(no subject)",
        "date": _header(headers, "Date"),
        "snippet": msg.get("snippet", ""),
        "unread": "UNREAD" in msg.get("labelIds", []),
        "labelIds": msg.get("labelIds", []),
    }
    if full:
        parsed["body"] = _extract_body(msg.get("payload", {}))
    return parsed


def list_messages(query: Optional[str] = None, label_ids: Optional[list[str]] = None, max_results: int = 25) -> list[dict]:
    svc = _service()
    resp = svc.users().messages().list(
        userId="me", q=query, labelIds=label_ids, maxResults=max_results
    ).execute()
    ids = [m["id"] for m in resp.get("messages", [])]
    results = []
    for mid in ids:
        full = svc.users().messages().get(
            userId="me", id=mid, format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()
    results.append(_parse_message(full))


def get_message(message_id: str) -> dict:
    svc = _service()
    full = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    return _parse_message(full, full=True)


def send_message(to: str, subject: str, body: str, thread_id: Optional[str] = None, in_reply_to_msg_id: Optional[str] = None) -> dict:
    svc = _service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    if in_reply_to_msg_id:
        # threading headers so replies show up in the same Gmail thread
        message["In-Reply-To"] = in_reply_to_msg_id
        message["References"] = in_reply_to_msg_id

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body_payload = {"raw": raw}
    if thread_id:
        body_payload["threadId"] = thread_id

    sent = svc.users().messages().send(userId="me", body=body_payload).execute()
    return {"id": sent["id"], "threadId": sent.get("threadId")}


def build_search_query(sender: Optional[str] = None, keyword: Optional[str] = None,
                        date_after: Optional[str] = None, date_before: Optional[str] = None,
                        unread_only: bool = False) -> str:
    """
    Builds a Gmail search query string (same syntax as the Gmail search box).
    date_after / date_before expected as YYYY/MM/DD.
    """
    parts = []
    if sender:
        parts.append(f"from:{sender}")
    if keyword:
        parts.append(keyword)
    if date_after:
        parts.append(f"after:{date_after}")
    if date_before:
        parts.append(f"before:{date_before}")
    if unread_only:
        parts.append("is:unread")
    return " ".join(parts)
