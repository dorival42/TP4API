from surprise import Dataset, Reader, SVD
import pandas as pd

# Charger les données MovieLens 100k
def load_data():
    url = "http://files.grouplens.org/datasets/movielens/ml-100k/u.data"
    column_names = ['user_id', 'item_id', 'rating', 'timestamp']
    data = pd.read_csv(url, sep='\t', names=column_names)
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[['user_id', 'item_id', 'rating']], reader)
    return dataset

# Initialiser et entraîner le modèle
model = SVD()

def train_model():
    dataset = load_data()
    trainset = dataset.build_full_trainset()
    model.fit(trainset)
    return {"message": "Modèle entraîné avec succès !"}

def get_recommendations(user_id: int, num_recommendations: int = 5):
    recommendations = []
    dataset = load_data()
    testset = dataset.build_full_trainset().build_testset()
    for movie_id in range(1, 1683):  # Les ID de films vont de 1 à 1682 dans ml-100k
        prediction = model.predict(user_id, movie_id)
        recommendations.append({"movie_id": movie_id, "predicted_rating": prediction.est})
    # Trier par note prédite et retourner les meilleures recommandations
    recommendations.sort(key=lambda x: x["predicted_rating"], reverse=True)
    return recommendations[:num_recommendations]
