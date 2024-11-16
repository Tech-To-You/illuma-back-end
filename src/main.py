from uuid import uuid4

from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore
import firebase_admin
import os
from dotenv import load_dotenv

from models.user import User
from models.history import AddHistory

load_dotenv()

cred_path = os.getenv("SERVICE_ACCOUNT_PATH")
if not cred_path:
    raise RuntimeError("O caminho para o arquivo de credenciais não está definido. Configure o SERVICE_ACCOUNT_PATH no .env.")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()



@app.post("/v1/user/create")
def create_user(user: User):    
    users_collection = db.collection("users")
    user_query = users_collection.where("email", "==", user.email).limit(1)
    user_res = user_query.get()[0]

    if user_res.exists:
        raise HTTPException(status_code=400, detail=f"Usuário '{user.email}' já existe!")
    
    user_id = str(uuid4())

    user_doc = users_collection.document(user_id)
    user_doc.set({
        "id": user_id,
        "email": user.email,
        "preferences": user.preferences,
        
    })
    
    histories_collection = db.collection("histories")
    histories_collection.document(user_doc.id).set({
        "user_id": user_doc.id,
        "history": []
    })

    return {"msg": f"Usuário '{usuario.nome}' criado com sucesso!", "user_id": user_doc.id}

 
@app.post("/v1/history/add-term")
def add_to_history(history: AddHistory):    
    users_collection = db.collection("users")
    user_query = users_collection.where("id", "==", history.user_id).limit(1)
    user_res = user_query.get()[0]

    if not user_res.exists:
        raise HTTPException(status_code=404, detail=f"Usuário com ID '{history.user_id}' não encontrado!")

    histories_collection = db.collection("histories")
    history_query = histories_collection.where("user_id", "==",history.user_id).limit(1)
    history_res = history_query.get()[0]

    history_data = history_res.to_dict()

    if not history_res.exists:
        history_data = {"user_id": history.user_id, "history": []}

    history_doc = histories_collection.document(history.user_id)

    history_data["history"].append(history.history_term)
    history_doc.set(history_data)

    return {"msg": "Histórico atualizado com sucesso!", "History": history_data}


@app.get("/v1/user/get/{user_id}")
def get_user(user_id: str):    
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail=f"Usuário com ID '{user_id}' não encontrado!")

    user_data = user_doc.to_dict()
    return {"user_id": user_id, "user": user_data}


@app.get("/v1/history/get/{user_id}")
def get_history(user_id: str):    
    history_doc = db.collection("histories").document(user_id).get()
    if not history_doc.exists:
        raise HTTPException(status_code=404, detail=f"Histórico para o usuário com ID '{user_id}' não encontrado!")

    history_data = history_doc.to_dict()
    return {"user_id": user_id, "history": history_data}