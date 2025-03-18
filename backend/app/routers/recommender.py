from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    TrainResponse, RecommendResponse, DatasetInfoResponse,
    UserDetailsResponse, MovieDetailsResponse, TopRatedMoviesResponse,
    MovieSearchResponse, PopularMoviesResponse
)
from app.services.recommendation_service import train_model, get_recommendations, load_data
from app.utils.data_loader import load_movie_metadata
import pandas as pd

router = APIRouter()

@router.post("/train", response_model=TrainResponse)
def train():
    """
    Entraîner le modèle de recommandation
    """
    return train_model()

@router.get("/recommend/{user_id}", response_model=RecommendResponse)
def recommend(user_id: int, num_recommendations: int = 5):
    recommendations = get_recommendations(user_id, num_recommendations)
    return {"user_id": user_id, "recommendations": recommendations}

@router.get("/dataset/info", response_model=DatasetInfoResponse)
def dataset_info():
    dataset = load_data()
    df = pd.DataFrame(dataset.raw_ratings, columns=['user_id', 'item_id', 'rating', 'timestamp'])
    num_users = df['user_id'].nunique()
    num_items = df['item_id'].nunique()
    num_ratings = len(df)
    return {"num_users": num_users, "num_movies": num_items, "num_ratings": num_ratings}

@router.get("/user/{user_id}/details", response_model=UserDetailsResponse)
def user_details(user_id: int):
    dataset = load_data()
    df = pd.DataFrame(dataset.raw_ratings, columns=['user_id', 'item_id', 'rating', 'timestamp'])
    user_data = df[df['user_id'] == user_id]
    return {"user_id": user_id, "rated_movies": user_data[['item_id', 'rating']].to_dict(orient='records')}

@router.get("/movie/{movie_id}/details", response_model=MovieDetailsResponse)
def movie_details(movie_id: int):
    dataset = load_data()
    df = pd.DataFrame(dataset.raw_ratings, columns=['user_id', 'item_id', 'rating', 'timestamp'])
    movie_data = df[df['item_id'] == movie_id]
    avg_rating = movie_data['rating'].mean()
    return {"movie_id": movie_id, "avg_rating": avg_rating, "num_ratings": len(movie_data)}

@router.get("/movies/top_rated", response_model=TopRatedMoviesResponse)
def top_rated_movies(num_movies: int = 10):
    dataset = load_data()
    df = pd.DataFrame(dataset.raw_ratings, columns=['user_id', 'item_id', 'rating', 'timestamp'])
    avg_ratings = df.groupby('item_id')['rating'].mean().reset_index()
    top_movies = avg_ratings.sort_values(by='rating', ascending=False).head(num_movies)
    return {"top_movies": top_movies.to_dict(orient='records')}

@router.get("/movies/search", response_model=MovieSearchResponse)
def search_movies(query: str):
    movies_df = load_movie_metadata()
    results = movies_df[movies_df['title'].str.contains(query, case=False)]
    return {"results": results.to_dict(orient='records')}

@router.get("/movies/popular", response_model=PopularMoviesResponse)
def popular_movies(num_movies: int = 10):
    dataset = load_data()
    df = pd.DataFrame(dataset.raw_ratings, columns=['user_id', 'item_id', 'rating', 'timestamp'])
    popularity = df.groupby('item_id')['rating'].count().reset_index()
    popular_movies = popularity.sort_values(by='rating', ascending=False).head(num_movies)
    return {"popular_movies": popular_movies.to_dict(orient='records')}
