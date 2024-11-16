from pydantic import BaseModel

from models.preferences import Preferences

class User(BaseModel):
    email: str
    preferences: Preferences