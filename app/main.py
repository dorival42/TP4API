from fastapi import FastAPI
from app.routers.recommender import router as recommender_router

app = FastAPI(title="Movie Recommendation API", version="1.0.0")

# Inclure les routeurs
app.include_router(recommender_router, prefix="/api", tags=["recommender"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de recommandation de films !"}
