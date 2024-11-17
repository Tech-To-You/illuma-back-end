import os
from dotenv import load_dotenv



import requests

load_dotenv()

articles_api_url  = os.getenv("ARTICLES_API")

def get_articles_by_keywords(keywords_groups):
  articles = []    
  for keywords in keywords_groups:    
    response = requests.get(f"{articles_api_url}/works?query={keywords}")    

    if response.status_code == 200:
      data = response.json()
      articles += data["message"]["items"]
  return articles
      