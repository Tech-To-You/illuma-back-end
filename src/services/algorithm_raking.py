#!/usr/bin/env python3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from typing import List
from models.papers import N_Paper


def simple_rank(query: str, n_paper: N_Paper):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    corpus = [paper.abstract for abstract in n_paper.abstracts]

    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarities = cosine_similarity(
        query_embedding.cpu().reshape(1, -1), corpus_embeddings.cpu()
    )

    ranking_indices = similarities.argsort()[0][::-1]

    ranked_results = [
        {
            "DOI": n_paper.abstracts[idx].DOI,
            "title": n_paper.abstracts[idx].title,
            "abstract": n_paper.abstracts[idx].abstract,
            "link": n_paper.abstracts[idx].link,
            "publication_year": n_paper.abstracts[idx].publication_year,
        }
        for idx in ranking_indices
    ]
    return ranked_results
