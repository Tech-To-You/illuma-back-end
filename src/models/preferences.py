from pydantic import BaseModel

class Preferences(BaseModel):
    theme: str
    email_updates: bool