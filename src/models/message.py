from pydantic import BaseModel

class GPTMessage(BaseModel):
    role: str
    content: str

class Message(BaseModel):
    prompt: str
    history: list[GPTMessage]
    is_first_message: bool