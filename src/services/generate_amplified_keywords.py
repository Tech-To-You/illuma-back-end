import os
import re
from dotenv import load_dotenv
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

load_dotenv()

dictionary_api_url = os.getenv("DICTIONARY_API")

def generate_keywords(prompt):
  stop_words = set(stopwords.words('portuguese'))
  word_tokens = word_tokenize(prompt)
  keywords = [w for w in word_tokens if not w.lower() in stop_words and w.isalpha()]
  return keywords

def generate_synonyms(keywords):  
  synonyms = keywords
  
  for keyword in keywords:
    response = requests.get(f"{dictionary_api_url}/word/{keyword}")
    
    if response.status_code == 200:
      data = response.json()
      
      if len(data) > 0:        
        xml = data[0]["xml"]

        pattern = r"<def>\s*(.*?)\s*</def>"
        definitions = re.findall(pattern, xml, re.DOTALL)

        str_definitions = str(definitions).replace("[", "").replace("]", "").replace(",", "")

        new_keywords = generate_keywords(str_definitions)
        synonyms = synonyms + new_keywords
  
  return list(synonyms)
    
      

def generate_amplified_keywords(prompt):
  keywords = generate_keywords(prompt)  
  amplified_keywords = generate_synonyms(keywords)

  return {"amplified_keywords": amplified_keywords, "original_keywords": keywords}
  

