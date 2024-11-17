from uuid import uuid4
from flask import Flask, jsonify, request, abort
from firebase_admin import credentials, firestore
import firebase_admin
import os

from dotenv import load_dotenv
from more_itertools import chunked

from services.algorithm_raking import simple_rank
from models.user import User
from models.history import AddHistory
from models.email import SendEmail

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

app = Flask(__name__)

@app.route("/v1/chat-bot", methods=["POST"])
def read_item():
    data = request.get_json()
    message = Message(**data)
    response = generate_response(message.prompt, message.history, message.is_first_message)
    return jsonify({"status": 200, "response": response})

@app.route("/v1/user/create", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(**data)
    users_collection = db.collection("users")
    user_query = users_collection.where("email", "==", user.email).limit(1)
    user_res = user_query.get()
    
    if user_res:
        abort(400, f"Usuário '{user.email}' já existe!")

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

    return jsonify({"msg": f"Usuário '{user.name}' criado com sucesso!", "user_id": user_doc.id})

@app.route("/v1/history/add-term", methods=["POST"])
def add_to_history():
    data = request.get_json()
    history = AddHistory(**data)
    users_collection = db.collection("users")
    user_query = users_collection.where("id", "==", history.user_id).limit(1)
    user_res = user_query.get()

    if not user_res:
        abort(404, f"Usuário com ID '{history.user_id}' não encontrado!")

    histories_collection = db.collection("histories")
    history_query = histories_collection.where("user_id", "==", history.user_id).limit(1)
    history_res = history_query.get()

    history_data = history_res[0].to_dict() if history_res else {"user_id": history.user_id, "history": []}
    history_doc = histories_collection.document(history.user_id)

    history_data["history"].append(history.history_term)
    history_doc.set(history_data)

    return jsonify({"msg": "Histórico atualizado com sucesso!", "History": history_data})

@app.route("/v1/user/get/<user_id>", methods=["GET"])
def get_user(user_id):
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        abort(404, f"Usuário com ID '{user_id}' não encontrado!")

    user_data = user_doc.to_dict()
    return jsonify({"user_id": user_id, "user": user_data})

@app.route("/v1/history/get/<user_id>", methods=["GET"])
def get_history(user_id):
    history_doc = db.collection("histories").document(user_id).get()
    if not history_doc.exists:
        abort(404, f"Histórico para o usuário com ID '{user_id}' não encontrado!")

    history_data = history_doc.to_dict()
    return jsonify({"user_id": user_id, "history": history_data})

@app.route("/v1/articles/get/<search_term>", methods=["GET"])
def get_articles(search_term):
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

    return jsonify({"articles": articles})

@app.route("/v1/email/send", methods=["POST"])
def send_email():
    data = request.get_json()
    email_props = SendEmail(**data)

    keywords_res = generate_amplified_keywords("Naruto")
    keywords_batch_size = len(keywords_res["original_keywords"])
    amplified_keywords = keywords_res["amplified_keywords"]

    batched_keywords = list(chunked(amplified_keywords, keywords_batch_size))
    
    formatted_keywords = [str(keywords_group).replace("[", "").replace("]","").replace(",", "") for keywords_group in batched_keywords]

    articles = get_articles_by_keywords(formatted_keywords)
    email = email_props.email_receiver
    email_sent_response = send_article_email(email, articles)

    return jsonify(email_sent_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
