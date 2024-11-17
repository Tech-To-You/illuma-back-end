from utils.generate_html_structure import generate_html_structure

def generate_article(article):
  title =  article["title"][0] if isinstance(article.get("title"), list) and len(article["title"]) > 0 else "Sem Título"
  publisher = article.get("publisher", "Desconhecido")
  doi = article["DOI"]

  article_creation_data = article["created"]
  article_date_parts = article_creation_data["date-parts"]
  publication_date = "/".join(map(str, article_date_parts[::-1])).replace(",", "/").replace(" ", "").replace("[", "").replace("]", "")
  
  authors = article.get("author", [])
  score = article["score"]

  references_count = article.get("references-count", 0)
  url = article.get("URL", "#")
  score = article.get("score", 0)

  html_title=f"<h1 class='article-title'>{title}</h1>"
  sub_heading = f"<h3 class='subheading'>Publicado por {publisher}. DOI: {doi}</h3>"

  authors_html = "".join(
    [f"<span class='author'>{author.get('family', '')} {author.get('given', '')}</span>" for author in authors]
  )


  additional_info = f"""
  <div class='additional-info'>
    <div class='rating'>
      <span class='rating-text'>Avaliado em {round(score, 1)}</span>
      <span class='rating-text'>Citações: {references_count}</span>
    </div>
    <div class='date-and-authors'> 
      <span class='publication-date'>{publication_date}</span>
      <div class='authors-wrapper'>
        {authors_html}
      </div>
    </div>
  </div>
"""
  
  access_button = f"<a href='{url}' target='_blank'><button class='access-button'>Acessar</button></a>"

  article_content = f"""
  <div class='article'>
  {html_title}
  {sub_heading}
  {additional_info}
  {access_button}
  </div>
"""
  
  return article_content



def generate_articles_as_html(articles):
  background_color = "#FFFFFF"
  font_color = "#212529"
  primary_color = "#1C1C5E"
  secondary_color = "#F16421"

  styles = """
body {
    background-color: background_color;
    margin: 0;
    font-family: 'Arial', sans-serif;
}

.article {
    background-color: background_color;
    border: 1px solid #E5E5E5;
    border-radius: 10px;
    padding: 20px;
    margin: 20px auto;
    width: 80%;
    max-width: 600px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.article-title {
    font-size: 18px;
    font-weight: 700;
    color: primary_color;
    text-align: center;
    margin-bottom: 10px;
}

.subheading {
    font-size: 14px;
    font-weight: 500;
    color: font_color;
    text-align: center;
    margin-bottom: 15px;
}

.additional-info {
    margin: 10px 0;
}

.rating-text {
    font-size: 12px;
    color: font_color;
}

.publication-date {
    font-size: 12px;
    color: font_color;
    margin-right: 10px;
}

.authors-wrapper {
    margin-top: 10px;
}

.author {
    font-size: 12px;
    color: font_color;
    margin-right: 10px;
}

.access-button {
    display: inline-block;
    background-color: primary_color;
    color: background_color;
    font-size: 14px;
    font-weight: 600;
    text-align: center;
    padding: 10px 20px;
    border-radius: 5px;
    text-decoration: none;
    border: none;
    cursor: pointer;
}

.access-button:hover {
    background-color: secondary_color;
}
""".replace("font_color", font_color).replace("primary_color", primary_color).replace("secondary_color", secondary_color).replace("background_color", background_color)


  articles_html = "".join([generate_article(article) for article in articles])
  description = "<p class='text'>Recomendação de artigos do CAPES com base nos seus gostos.</p>"


  body_html = description + articles_html

  html_content = generate_html_structure(styles, body_html)

  return html_content
