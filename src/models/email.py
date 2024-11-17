from pydantic import BaseModel

class SendEmail(BaseModel):
  email_receiver: str  