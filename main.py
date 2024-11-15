from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from firebase_admin import credentials, firestore
import firebase_admin
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Inicializa o Firebase com as credenciais do serviço
cred_path = os.getenv("SERVICE_ACCOUNT_PATH")
if not cred_path:
    raise RuntimeError("O caminho para o arquivo de credenciais não está definido. Configure o SERVICE_ACCOUNT_PATH no .env.")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Inicializa o Firestore
db = firestore.client()

app = FastAPI()

# Models
class User(BaseModel):
    nome: str
    preferencias: dict  # Exemplo: {"tema": "claro", "notificacoes": True}

class Historico(BaseModel):
    user_id: str
    eventos: list  # Exemplo: [{"tipo": "login", "data": "2024-11-15"}]


@app.post("/usuarios")
def criar_usuario(usuario: User):
    # Verifica se o usuário já existe no Firestore
    users_collection = db.collection("users")
    user_query = users_collection.where("nome", "==", usuario.nome).get()

    if user_query:
        raise HTTPException(status_code=400, detail=f"Usuário '{usuario.nome}' já existe!")

    # Cria o novo usuário no Firestore
    user_doc = users_collection.document()
    user_doc.set({
        "nome": usuario.nome,
        "preferencias": usuario.preferencias
    })

    # Cria um histórico vazio para o novo usuário
    histories_collection = db.collection("histories")
    histories_collection.document(user_doc.id).set({
        "user_id": user_doc.id,
        "eventos": []
    })

    return {"msg": f"Usuário '{usuario.nome}' criado com sucesso!", "user_id": user_doc.id}


@app.post("/historico")
def adicionar_historico(historico: Historico):
    # Verifica se o usuário existe no Firestore
    user_doc = db.collection("users").document(historico.user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail=f"Usuário com ID '{historico.user_id}' não encontrado!")

    # Adiciona o evento ao histórico do usuário
    histories_collection = db.collection("histories")
    history_doc = histories_collection.document(historico.user_id)

    history_data = history_doc.get().to_dict()
    if not history_data:
        history_data = {"user_id": historico.user_id, "eventos": []}

    history_data["eventos"].extend(historico.eventos)
    history_doc.set(history_data)

    return {"msg": "Histórico atualizado com sucesso!", "historico": history_data}


@app.get("/usuarios/{user_id}")
def obter_usuario(user_id: str):
    # Obtém os dados do usuário no Firestore
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail=f"Usuário com ID '{user_id}' não encontrado!")

    user_data = user_doc.to_dict()
    return {"user_id": user_id, "usuario": user_data}


@app.get("/historico/{user_id}")
def obter_historico(user_id: str):
    # Obtém o histórico do usuário no Firestore
    history_doc = db.collection("histories").document(user_id).get()
    if not history_doc.exists:
        raise HTTPException(status_code=404, detail=f"Histórico para o usuário com ID '{user_id}' não encontrado!")

    history_data = history_doc.to_dict()
    return {"user_id": user_id, "historico": history_data}
