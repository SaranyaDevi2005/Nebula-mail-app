"""
The AI assistant: turns natural language into a UI action.

Design: the LLM only ever picks a *tool* (compose_email / search_emails /
open_email / reply_to_email) with structured arguments — it never freeforms
UI state. This backend then actually executes that tool against Gmail
(search, fetch, etc.) and hands the frontend one clean "action" object to
apply to its state. That keeps the LLM's job small (intent -> structured
call) and keeps all Gmail-specific logic in one place (gmail_service.py).
"""
import json
from datetime import datetime, timedelta

from groq import Groq

from . import config, gmail_service
from .models import AssistantContext

client = Groq(api_key=config.GROQ_API_KEY)

MODEL = "openai/gpt-oss-20b"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "compose_email",
            "description": "Open the compose view and pre-fill an email the user wants to write. Use this whenever the user asks to send/write/draft an email to someone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search or filter the inbox. Use for requests like 'show emails from the last 10 days', 'find the email from Sarah about the project update', 'show only unread emails from this week'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender name or email to filter by, if mentioned"},
                    "keyword": {"type": "string", "description": "Subject/body keyword to search for, if mentioned"},
                    "days_back": {"type": "integer", "description": "If the user gives a relative time window (e.g. 'last 10 days', 'this week'), the number of days back to search"},
                    "unread_only": {"type": "boolean", "description": "True if the user only wants unread emails"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_email",
            "description": "Open one specific email in the detail view, e.g. 'open the latest email from David'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender name or email, if mentioned"},
                    "keyword": {"type": "string", "description": "Subject/body keyword to identify the email, if mentioned"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_email",
            "description": "Reply to the email the user is currently viewing. Use for 'reply to this', 'respond and say...'. Requires an email to already be open.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {"type": "string", "description": "What the reply should say, if the user specified content; otherwise a short generic acknowledgement."},
                },
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are the assistant inside a mail web app. Your job is to translate the \
user's natural-language request into exactly one tool call that controls the UI. \
Always call a tool when the request is actionable (composing, searching, opening, replying). \
Only respond with plain text (no tool call) for greetings or questions that aren't about \
controlling the mail app."""


def _resolve_days_back(days_back: int | None) -> str | None:
    if not days_back:
        return None
    d = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    return d


def _run_search(args: dict) -> dict:
    query = gmail_service.build_search_query(
        sender=args.get("sender"),
        keyword=args.get("keyword"),
        date_after=_resolve_days_back(args.get("days_back")),
        unread_only=bool(args.get("unread_only")),
    )
    emails = gmail_service.list_messages(query=query or None, max_results=25)
    return {
        "type": "search_results",
        "payload": {"emails": emails, "query": query},
    }


def _run_open(args: dict) -> dict:
    query = gmail_service.build_search_query(sender=args.get("sender"), keyword=args.get("keyword"))
    matches = gmail_service.list_messages(query=query or None, max_results=1)
    if not matches:
        return {"type": "none", "payload": {}}
    full = gmail_service.get_message(matches[0]["id"])
    return {"type": "open_email", "payload": {"email": full}}


def _run_compose(args: dict) -> dict:
    return {
        "type": "compose_email",
        "payload": {
            "to": args.get("to", ""),
            "subject": args.get("subject", ""),
            "body": args.get("body", ""),
        },
    }


def _run_reply(args: dict, context: AssistantContext) -> dict:
    if not context.open_email_id:
        return {"type": "none", "payload": {}, "text": "There's no email open to reply to — open one first."}
    original = gmail_service.get_message(context.open_email_id)
    instructions = args.get("instructions", "").strip()
    quoted = "\n".join(f"> {line}" for line in original["body"].splitlines()[:6])
    body = f"{instructions}\n\nOn {original['date']}, {original['sender']} wrote:\n{quoted}" if instructions else f"\n\nOn {original['date']}, {original['sender']} wrote:\n{quoted}"
    subject = original["subject"] if original["subject"].lower().startswith("re:") else f"Re: {original['subject']}"
    return {
        "type": "compose_email",
        "payload": {
            "to": original["sender"],
            "subject": subject,
            "body": body,
            "thread_id": original["threadId"],
            "in_reply_to_msg_id": original["id"],
        },
    }


def call_assistant(message: str, context: AssistantContext) -> dict:
    context_note = f"Current view: {context.current_view}. Open email id: {context.open_email_id or 'none'}."
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context_note},
            {"role": "user", "content": message},
        ],
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.2,
    )

    choice = response.choices[0].message

    if not choice.tool_calls:
        return {"reply": choice.content or "Okay.", "action": {"type": "none", "payload": {}}}

    call = choice.tool_calls[0]
    name = call.function.name
    args = json.loads(call.function.arguments or "{}")

    if name == "compose_email":
        action = _run_compose(args)
        reply = f"I've filled in a draft to {args.get('to', '')} — check the compose panel and hit send when ready."
    elif name == "search_emails":
        action = _run_search(args)
        reply = f"Found {len(action['payload']['emails'])} matching email(s)."
    elif name == "open_email":
        action = _run_open(args)
        if action["type"] == "none":
            reply = "I couldn't find a matching email."
        else:
            reply = f"Opened: {action['payload']['email']['subject']}"
    elif name == "reply_to_email":
        action = _run_reply(args, context)
        reply = action.pop("text", "I've drafted a reply — review it and send.")
    else:
        action = {"type": "none", "payload": {}}
        reply = "I'm not sure how to do that yet."

    return {"reply": reply, "action": action}
