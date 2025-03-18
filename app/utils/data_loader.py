import pandas as pd

def load_movie_metadata():
    # Charger les métadonnées des films (exemple avec ml-100k)
    url = "http://files.grouplens.org/datasets/movielens/ml-100k/u.item"
    column_names = ['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL']
    return pd.read_csv(url, sep='|', names=column_names, encoding='latin1', usecols=range(5))
