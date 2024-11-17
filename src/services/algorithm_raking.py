from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.papers import N_Paper

from utils.get_title import get_title

def simple_rank(query: str, n_paper: N_Paper):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    corpus = [article.get("abstract", get_title(article)) for article in n_paper]

    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarities = cosine_similarity(
        query_embedding.cpu().reshape(1, -1), corpus_embeddings.cpu()
    )

    ranking_indices = similarities.argsort()[0][::-1]

    ranked_results =[n_paper[i] for i in ranking_indices]
    
    return ranked_results
