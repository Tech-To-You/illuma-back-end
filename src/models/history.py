from pydantic import BaseModel

class History(BaseModel):
    user_id: str
    history: list[str]

class AddHistory(BaseModel):
    user_id: str
    history_term: str