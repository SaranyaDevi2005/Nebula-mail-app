from typing import Optional
from pydantic import BaseModel


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None
    in_reply_to_msg_id: Optional[str] = None


class AssistantContext(BaseModel):
    current_view: str = "inbox"          # "inbox" | "sent" | "compose" | "detail"
    open_email_id: Optional[str] = None   # id of the email currently in EmailDetail, if any


class AssistantRequest(BaseModel):
    message: str
    context: AssistantContext = AssistantContext()
