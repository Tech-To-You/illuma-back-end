from typing import List
from pydantic import BaseModel


class Paper(BaseModel):
    DOI: str
    title: str
    link: str
    publication_year: int
    abstract: str


class N_Paper(BaseModel):
    abstracts: List[Paper]
