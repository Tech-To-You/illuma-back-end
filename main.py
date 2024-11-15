from typing import Union

from fastapi import FastAPI, Request

from pydantic import BaseModel

app = FastAPI()


class Nome(BaseModel):
    nome: str


lista_de_nomes = []


@app.post("/nomes")
def registrar_nome(novo_nome: Nome):
    lista_de_nomes.append(novo_nome.dict())
    return {"msg": f"Usuário {novo_nome.nome} cadastrado!"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
