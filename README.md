# Nebula Mail — AI-Powered Mail Web App

A mail client (Gmail-backed) with an assistant panel that controls the UI directly:
composing, filling forms, filtering the inbox, opening emails, and drafting replies —
all from natural language, not just answering questions in a chat box.

Built for the Nebula KnowLab hiring task.

## Architecture

```
frontend (React + Vite + Tailwind)
  │  REST calls
  ▼
backend (FastAPI)
  ├─ auth.py           Google OAuth 2.0 flow, local token storage
  ├─ gmail_service.py  Gmail API wrapper (list / get / send / search) — single source
  │                    of truth for "what an email looks like", used by both the
  │                    normal UI endpoints and the assistant
  ├─ assistant.py       Groq (GPT-OSS 20B) tool-calling: turns a natural-language
  │                     message into ONE structured tool call, executes it against
  │                     gmail_service, and returns a single "action" object
  └─ main.py             Route wiring
```

**Why tool-calling instead of a framework like CopilotKit:** the assistant never
free-forms UI changes — it picks from a fixed set of tools (`compose_email`,
`search_emails`, `open_email`, `reply_to_email`) with structured arguments. The
backend executes the tool for real (actually searches Gmail, actually fetches the
message) and sends the frontend one `action: { type, payload }` object. The
frontend's reducer (`MailContext.jsx`) just applies that action to state — the
same code path the UI's own buttons and filters use. This keeps the LLM's job
narrow and auditable instead of letting it emit arbitrary UI instructions.

## Setup

### 1. Google Cloud / Gmail API

1. Create a project at console.cloud.google.com, enable the **Gmail API**.
2. Configure the OAuth consent screen as **External**, add your own Google account
   as a **test user** (this skips Google's verification review — fine for a demo).
3. Create an **OAuth 2.0 Client ID** (Web application) with redirect URI
   `http://localhost:8000/auth/callback`.
4. Copy the client ID/secret into `backend/.env` (see below).

### 2. Groq API

Get a free key at console.groq.com and put it in `backend/.env`.

### 3. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/auth/login` once to grant access — this writes
`backend/token.json`, which the app reuses (and auto-refreshes) after that.

### 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # defaults are fine for local dev
npm run dev
```

Open `http://localhost:5173`.

## Trade-offs (given the time constraint)

- **Real-time sync is polling (15s), not Gmail Pub/Sub push.** Push requires a
  verified GCP domain, a Pub/Sub topic, and a public webhook endpoint — a lot of
  infra for a short build. Polling satisfies "no manual refresh" with a fraction
  of the setup; swapping in Pub/Sub later only touches `gmail_service.py` and
  wouldn't change the frontend at all.
- **Single-user auth, token stored in a local file** rather than per-session/DB
  storage. Fine for a demo account; the first change needed for multi-user
  production use is per-session credential storage.
- **Reply quoting is a simple text excerpt**, not full HTML quote formatting.

## What I'd improve with more time

- Real Gmail push notifications (Pub/Sub + webhook) instead of polling
- Thread/conversation view instead of flat message lists
- Multi-user session-based auth
- Streaming assistant responses instead of a single request/response round trip
- Tests for `gmail_service.py` query building and `assistant.py` tool routing

## Demo

_Add a short screen recording or screenshots here showing the assistant filling
the compose form and updating the inbox live._
