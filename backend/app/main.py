from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config, gmail_service
from .auth import router as auth_router
from .assistant import call_assistant
from .models import SendEmailRequest, AssistantRequest

app = FastAPI(title="Nebula Mail API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/inbox")
def inbox(max_results: int = 25):
    try:
        return gmail_service.list_messages(label_ids=["INBOX"], max_results=max_results)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/sent")
def sent(max_results: int = 25):
    try:
        return gmail_service.list_messages(label_ids=["SENT"], max_results=max_results)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/messages/{message_id}")
def get_message(message_id: str):
    try:
        return gmail_service.get_message(message_id)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/send")
def send(req: SendEmailRequest):
    try:
        return gmail_service.send_message(
            to=req.to,
            subject=req.subject,
            body=req.body,
            thread_id=req.thread_id,
            in_reply_to_msg_id=req.in_reply_to_msg_id,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/search")
def search(sender: str = None, keyword: str = None, date_after: str = None,
           date_before: str = None, unread_only: bool = False):
    try:
        query = gmail_service.build_search_query(sender, keyword, date_after, date_before, unread_only)
        return gmail_service.list_messages(query=query or None)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/assistant")
def assistant(req: AssistantRequest):
    try:
        return call_assistant(req.message, req.context)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}
