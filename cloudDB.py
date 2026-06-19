from fastapi import FastAPI
import json
import pandas as pd
from pinecone import Pinecone

app = FastAPI()

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None

    def _load_model(self):

        if self.model is None:

            # Lazy import
            from sentence_transformers import (
                SentenceTransformer
            )

            self.model = (
                SentenceTransformer(
                    self.model_name
                )
            )
        
    def generate_embeddings(self, texts):
        self._load_model()
        embeddings = self.model.encode(texts)
        return embeddings

embedding = EmbeddingManager()
def clean_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def extract_names(json_string):
    if pd.isna(json_string) or json_string == "":
        return ""

    try:
        data = json.loads(json_string)

        names = [item["name"] for item in data if "name" in item]

        return ", ".join(names)

    except Exception:
        return ""


@app.get("/retreiver-movies")
def getRelatedMovies():
    df = pd.read_csv("movies.csv")
    pc = Pinecone(api_key="pcsk_6TrCS2_4LiK45erZMq9j4ncT6Nzi8HUJQBxD3Hk3KK2ZGDgn6HjzA2tokYGR7xgjGnpMr6")
    index = pc.Index(host="https://test-ul0krd9.svc.aped-4627-b74a.pinecone.io")
    matched_movies = df.loc[df["title"] == "Furious 7"]

    if matched_movies.empty:
        return {"error": "Movie not found", "title": "Furious 7"}

    movie = matched_movies.iloc[0]
    title = movie.get("title", "")
    overview = movie.get("overview", "")
    tagline = movie.get("tagline", "")

    genres = extract_names(movie.get("genres", ""))
    keywords = extract_names(movie.get("keywords", ""))
    production_companies = extract_names(movie.get("production_companies", ""))
    combined_text = f"""
        Movie Title:
        {title}

        Genres:
        {genres}

        This movie belongs to:
        {genres}

        Overview:
        {overview}

        Themes and Keywords:
        {keywords}

        Keywords:
        {keywords}

        Tagline:
        {tagline}

        Produced By:
        {production_companies}
        """.strip()
    
    query_embedding = embedding.generate_embeddings([combined_text])[0]

    # Convert numpy array to list
    query_embedding = query_embedding.tolist()
    results = index.query(
        namespace="movie-namespace",
        vector=query_embedding, 
        top_k=5,
        include_metadata=True,
        include_values=False
    )   
    formatted_results = []

    for match in results["matches"]:

        formatted_results.append({
            "score": match["score"],
            # "document_id": match["metadata"]["document_id"],
            "genres": match["metadata"]["genres"],
            "title": match["metadata"]["title"]
        })

    return {
        "query": title,
        "results": formatted_results
    }
