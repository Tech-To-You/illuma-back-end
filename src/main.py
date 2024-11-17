from uuid import uuid4

from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore
import firebase_admin
import os

from services.algorithm_raking import simple_rank

from dotenv import load_dotenv
from more_itertools import chunked

from models.user import User
from models.history import AddHistory
from models.email import SendEmail
from models.papers import Paper

from services.generate_amplified_keywords import generate_amplified_keywords
from services.get_articles import get_articles_by_keywords
from services.send_article_email import send_article_email

from services.chat_bot import generate_response
from models.message import Message

load_dotenv()

cred_path = os.getenv("SERVICE_ACCOUNT_PATH")
if not cred_path:
    raise RuntimeError(
        "O caminho para o arquivo de credenciais não está definido. Configure o SERVICE_ACCOUNT_PATH no .env."
    )

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

@app.post("/v1/chat-bot")
async def read_item(message: Message):
    response = generate_response(message.prompt, message.history, message.is_first_message);  
    return {"status": 200, "response": response}    
    

@app.post("/v1/user/create")
def create_user(user: User):
    users_collection = db.collection("users")
    user_query = users_collection.where("email", "==", user.email).limit(1)
    user_res = user_query.get()[0]

    if user_res.exists:
        raise HTTPException(
            status_code=400, detail=f"Usuário '{user.email}' já existe!"
        )

    user_id = str(uuid4())

    user_doc = users_collection.document(user_id)
    user_doc.set(
        {
            "id": user_id,
            "email": user.email,
            "preferences": user.preferences,
        }
    )
  
    histories_collection = db.collection("histories")
    histories_collection.document(user_doc.id).set(
        {"user_id": user_doc.id, "history": []}
    )

    return {"msg": f"Usuário '{user.name}' criado com sucesso!", "user_id": user_doc.id}

@app.post("/v1/history/add-term")
def add_to_history(history: AddHistory):
    users_collection = db.collection("users")
    user_query = users_collection.where("id", "==", history.user_id).limit(1)
    user_res = user_query.get()[0]

    if not user_res.exists:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário com ID '{history.user_id}' não encontrado!",
        )

    histories_collection = db.collection("histories")
    history_query = histories_collection.where("user_id", "==", history.user_id).limit(
        1
    )
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
        raise HTTPException(
            status_code=404, detail=f"Usuário com ID '{user_id}' não encontrado!"
        )

    user_data = user_doc.to_dict()
    return {"user_id": user_id, "user": user_data}


@app.get("/v1/history/get/{user_id}")
def get_history(user_id: str):
    history_doc = db.collection("histories").document(user_id).get()
    if not history_doc.exists:
        raise HTTPException(
            status_code=404,
            detail=f"Histórico para o usuário com ID '{user_id}' não encontrado!",
        )

    history_data = history_doc.to_dict()
    return {"user_id": user_id, "history": history_data}


@app.get("/v1/articles/get/{search_term}")
def get_articles(search_term: str):
    keywords_res = generate_amplified_keywords(search_term)
    keywords_batch_size = len(keywords_res["original_keywords"])
    amplified_keywords = keywords_res["amplified_keywords"]

    batched_keywords = list(chunked(amplified_keywords, keywords_batch_size))

    formatted_keywords = [
        str(keywords_group).replace("[", "").replace("]", "").replace(",", "")
        for keywords_group in batched_keywords
    ]

    articles = get_articles_by_keywords(formatted_keywords)

    articles = simple_rank(search_term, articles)    

    # for n_paper in articles:
    #     paper = Paper(
    #         DOI=n_paper.get("DOI", ""),
    #         title=n_paper.get("title", [""])[0],
    #         link=n_paper.get("URL", ""),
    #         publication_year=n_paper.get("issued", {}).get("data-parts", [[None]])[0][
    #             0
    #         ],
    #         abstract=n_paper.get("abstract", ""),
    #     )
    #     papers.append(paper)    
    
    return { "articles": articles }

@app.post("/v1/email/send")
def send_email(email_props: SendEmail):

    keywords_res = generate_amplified_keywords("Naruto")
    keywords_batch_size = len(keywords_res["original_keywords"])
    amplified_keywords = keywords_res["amplified_keywords"]
    
    batched_keywords = list(chunked(amplified_keywords, keywords_batch_size))
    
    formatted_keywords = [str(keywords_group).replace("[", "").replace("]","").replace(",", "") for keywords_group in batched_keywords]


    articles = get_articles_by_keywords(formatted_keywords)

    email = email_props.email_receiver
    
        

    email_sent_response = send_article_email(email, articles)

    return email_sent_response
