#!/usr/bin/env python3  # Spécifie l'interpréteur Python à utiliser
import os  
import sys 
import pandas as pd  
from sqlalchemy import create_engine, text  # Outils pour interagir avec une base de données SQL
from sqlalchemy.exc import OperationalError  # Exception pour les erreurs de connexion SQLAlchemy
from loguru import logger  

# Import SQLAlchemy models
from models import Base, Movie, Rating  # Importation des modèles SQLAlchemy définis

# Configure logger
logger.remove()  # Supprime les configurations de journalisation par défaut
logger.add(sys.stderr, level="INFO")  # Ajoute une sortie de journalisation sur stderr avec le niveau INFO

def get_db_engine():
    """
    Crée et retourne un moteur SQLAlchemy pour la connexion à PostgreSQL.
    """
    user = os.environ.get("POSTGRES_USER", "postgres")  # Récupère l'utilisateur PostgreSQL depuis les variables d'environnement
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")  # Récupère le mot de passe PostgreSQL
    ## Si on requette depuis un container docker le host est le nom du service docker (défini dans le docker-compose.yml)
    ## Mais si on voudrait se connecter depuis l'ordinateur on doit utiliser localhost donc pour tester le script changer cette ligne par host = "localhost"
    # host = "postgres"  # Nom du service Docker pour PostgreSQL
    host = "localhost"  # host base de données en dehors du container
    port = os.environ.get("POSTGRES_PORT", "5432")  # Récupère le port PostgreSQL
    database = os.environ.get("POSTGRES_DB", "moviesdb")  # Récupère le nom de la base de données

    # Construit l'URL de connexion à PostgreSQL
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(db_url)  # Retourne un moteur SQLAlchemy

def create_db_schema(engine):
    """
    Crée le schéma de la base de données à partir des modèles SQLAlchemy définis.
    """
    try:
        logger.info("Creating database schema...")  # Journalise le début de la création du schéma
        Base.metadata.create_all(engine)  # Crée toutes les tables définies dans les modèles SQLAlchemy
        logger.success("Database schema created successfully")  # Journalise le succès de la création
    except Exception:  # Capture toute exception
        logger.exception("Error creating database schema")  # Journalise l'erreur
        raise  # Relance l'exception

def import_data_with_pandas(engine, file_path, table_name, chunksize):
    """
    Importe les données d'un fichier CSV dans une table PostgreSQL en utilisant pandas.
    """
    try:
        logger.info(f"Importing data from {file_path} into {table_name} table")  # Journalise le début de l'importation
        df = pd.read_csv(file_path)  # Charge le fichier CSV dans un DataFrame pandas
        logger.info(f"Found {len(df)} records in CSV file")  # Journalise le nombre d'enregistrements trouvés
        
        # Insère les données dans la table cible par lots
        df.to_sql(
            table_name,  # Nom de la table cible
            engine,  # Moteur SQLAlchemy pour la connexion
            if_exists='append',  # Ajoute les données à la table existante
            index=False,  # N'insère pas l'index du DataFrame
            chunksize=chunksize,  # Nombre d'enregistrements par lot
            method='multi'  # Utilise une méthode d'insertion optimisée
        )
        logger.success(f"Imported {len(df)} records into {table_name} table")  # Journalise le succès de l'importation
        return len(df)  # Retourne le nombre total d'enregistrements importés
    except Exception:  # Capture toute exception
        logger.exception(f"Error importing data from {file_path} to {table_name}")  # Journalise l'erreur
        raise  # Relance l'exception

def create_indexes(engine):
    """
    Crée des index sur les tables pour améliorer les performances des requêtes.
    """
    try:
        logger.info("Creating database indexes...")  # Journalise le début de la création des index
        
        with engine.connect() as connection:  # Établit une connexion à la base de données
            # Crée un index sur la colonne user_id de la table ratings
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)"
            ))
            
            # Crée un index sur la colonne movie_id de la table ratings
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id)"
            ))
            
        logger.success("Database indexes created successfully")  # Journalise le succès de la création des index
    except Exception:  # Capture toute exception
        logger.exception("Error creating database indexes")  # Journalise l'erreur
        raise  # Relance l'exception

def main():
    """
    Fonction principale qui orchestre le processus complet d'importation des données.
    """
    try:
        data_dir = "/home/alinux/projects/m2/tp4/data"  # Répertoire contenant les fichiers CSV
        movies_path = os.path.join(data_dir, "movies_metadata.csv")  # Chemin vers le fichier des films
        ratings_path = os.path.join(data_dir, "ratings.csv")  # Chemin vers le fichier des évaluations
        
        logger.info("Connecting to PostgreSQL database...")  # Journalise le début de la connexion
        try:
            engine = get_db_engine()  # Crée le moteur de connexion à la base de données
            with engine.connect() as connection:  # Teste la connexion
                connection.execute(text("SELECT 1")).fetchone()  # Exécute une requête simple
            logger.info("Successfully connected to PostgreSQL")  # Journalise le succès de la connexion
        except OperationalError:  # Capture les erreurs de connexion
            logger.exception("Failed to connect to PostgreSQL")  # Journalise l'erreur
            sys.exit(1)  # Quitte le programme avec un code d'erreur
        
        create_db_schema(engine)  # Crée le schéma de la base de données
        import_data_with_pandas(engine, movies_path, 'movies', chunksize=1000)  # Importe les données des films
        import_data_with_pandas(engine, ratings_path, 'ratings', chunksize=5000)  # Importe les données des évaluations
        create_indexes(engine)  # Crée les index
        
        logger.success("Data import completed successfully")  # Journalise le succès du processus
    except Exception:  # Capture toute exception
        logger.exception("Error in data import process")  # Journalise l'erreur
        sys.exit(1)  # Quitte le programme avec un code d'erreur

if __name__ == "__main__":  # Point d'entrée du script
    main()  # Appelle la fonction principale
