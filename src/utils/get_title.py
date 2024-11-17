

def get_title(article):
  return article["title"][0] if isinstance(article.get("title"), list) and len(article["title"]) > 0 else "Sem Título"