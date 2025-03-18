from pydantic import BaseModel
from typing import List, Optional

class TrainResponse(BaseModel):
    message: str

class RecommendRequest(BaseModel):
    user_id: int
    num_recommendations: Optional[int] = 5

class Recommendation(BaseModel):
    movie_id: int
    predicted_rating: float

class RecommendResponse(BaseModel):
    user_id: int
    recommendations: List[Recommendation]

class DatasetInfoResponse(BaseModel):
    num_users: int
    num_movies: int
    num_ratings: int

class UserDetailsResponse(BaseModel):
    user_id: int
    rated_movies: List[dict]

class MovieDetailsResponse(BaseModel):
    movie_id: int
    avg_rating: float
    num_ratings: int

class TopRatedMoviesResponse(BaseModel):
    top_movies: List[dict]

class MovieSearchResponse(BaseModel):
    results: List[dict]

class PopularMoviesResponse(BaseModel):
    popular_movies: List[dict]

