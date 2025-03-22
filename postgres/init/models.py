from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey  # Importation des types de colonnes et des clés étrangères
from sqlalchemy.ext.declarative import declarative_base  # Importation pour définir une base de modèles SQLAlchemy

Base = declarative_base()  # Création d'une classe de base pour tous les modèles SQLAlchemy

class Movie(Base):  # Définition du modèle pour la table 'movies'
    __tablename__ = 'movies'  # Nom de la table dans la base de données
    
    movie_id = Column(Integer, primary_key=True)  # Colonne 'movie_id' de type entier, clé primaire
    title = Column(String(255), nullable=False)  # Colonne 'title' de type chaîne de caractères, non nulle
    genres = Column(String(255), nullable=False)  # Colonne 'genres' de type chaîne de caractères, non nulle
    
    def __repr__(self):  # Méthode pour représenter l'objet sous forme de chaîne
        return f"<Movie(movie_id={self.movie_id}, title='{self.title}')>"

class Rating(Base):  # Définition du modèle pour la table 'ratings'
    __tablename__ = 'ratings'  # Nom de la table dans la base de données
    
    user_id = Column(Integer, primary_key=True)  # Colonne 'user_id' de type entier, clé primaire
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), primary_key=True)  # Colonne 'movie_id', clé étrangère vers 'movies.movie_id', clé primaire composite
    rating = Column(Float, nullable=False)  # Colonne 'rating' de type flottant, non nulle
    timestamp = Column(BigInteger)  # Colonne 'timestamp' de type entier long, peut être nulle
    
    def __repr__(self):  # Méthode pour représenter l'objet sous forme de chaîne
        return f"<Rating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"
