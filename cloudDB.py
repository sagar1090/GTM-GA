from fastapi import FastAPI
import json
import pandas as pd
from pinecone import Pinecone

app = FastAPI()

@app.get("/retreiver-movies")
def getRelatedMovies():
    df = pd.read_csv("movies.csv")
    pc = Pinecone(api_key="pcsk_6TrCS2_4LiK45erZMq9j4ncT6Nzi8HUJQBxD3Hk3KK2ZGDgn6HjzA2tokYGR7xgjGnpMr6")
    index = pc.Index(host="https://test-ul0krd9.svc.aped-4627-b74a.pinecone.io")
    matched_movies = df.loc[df["title"] == "Furious 7"]

    if matched_movies.empty:
        return {"error": "Movie not found", "title": "Furious 7"}

    movie = matched_movies.iloc[0]
    movie_id = str(movie.get("id", ""))
    fetch_result = index.fetch(
    ids=[movie_id],
    namespace="movie-namespace"
    )
    query_vector = (
    fetch_result
    ["vectors"]
    [movie_id]
    ["values"]
    )
    results = index.query(
        namespace="movie-namespace",
        vector=query_vector, 
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
