from firebase_admin import credentials, firestore
import firebase_admin
import os
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv('SERVICE_ACCOUNT_PATH')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)


db = firestore.client()
