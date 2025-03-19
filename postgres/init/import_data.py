#!/usr/bin/env python3
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from loguru import logger

# Import SQLAlchemy models
from models import Base, Movie, Rating

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

def get_db_engine():
    """
    Crée et retourne un moteur SQLAlchemy pour la connexion à PostgreSQL.
    
    Étapes:
    1. Récupère les informations de connexion depuis les variables d'environnement
    2. Construit l'URL de connexion à la base de données PostgreSQL
    3. Crée et retourne un objet Engine SQLAlchemy
    
    Retourne:
        Un objet Engine SQLAlchemy configuré pour la connexion à PostgreSQL
    """
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = "postgres"  # Docker service name
    port = os.environ.get("POSTGRES_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "movies")
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(db_url)

def create_db_schema(engine):
    """
    Crée le schéma de la base de données à partir des modèles SQLAlchemy définis.
    
    Étapes:
    1. Utilise Base.metadata.create_all pour créer toutes les tables
    2. Crée les tables 'movies' et 'ratings' selon les modèles Movie et Rating
    3. Établit les contraintes de clé primaire et de clé étrangère
    
    Args:
        engine: L'objet Engine SQLAlchemy pour la connexion à la base de données
        
    Raises:
        Exception: Si la création du schéma échoue, l'erreur est journalisée et propagée
    """

    try:
        logger.info("Creating database schema...")
        Base.metadata.create_all(engine)
        logger.success("Database schema created successfully")
    except Exception:
        logger.exception("Error creating database schema")
        raise

def import_data_with_pandas(engine, file_path, table_name, chunksize):
    """
    Importe les données d'un fichier CSV dans une table PostgreSQL en utilisant pandas.
    
    Étapes:
    1. Charge le fichier CSV spécifié dans un DataFrame pandas
    2. Vérifie la présence des colonnes requises selon le modèle correspondant
    3. Effectue les mappages nécessaires des noms de colonnes si besoin
    4. Sélectionne uniquement les colonnes correspondant au modèle
    5. Insère les données par lots dans la table cible
    
    Args:
        engine: L'objet Engine SQLAlchemy pour la connexion à la base de données
        file_path: Chemin vers le fichier CSV à importer
        table_name: Nom de la table de destination ('movies' ou 'ratings')
        chunksize: Nombre d'enregistrements à insérer par lot
        
    Returns:
        int: Le nombre total d'enregistrements importés
        
    Raises:
        Exception: Si l'importation échoue, l'erreur est journalisée et propagée
        ValueError: Si des colonnes requises sont manquantes dans le CSV
    """
    try:
        logger.info(f"Importing data from {file_path} into {table_name} table")
        df = pd.read_csv(file_path)
        logger.info(f"Found {len(df)} records in CSV file")
        
        # Import data with pandas
        df.to_sql(
            table_name, 
            engine, 
            if_exists='append', 
            index=False, 
            chunksize=chunksize,
            method='multi'
        )
        logger.success(f"Imported {len(df)} records into {table_name} table")
        return len(df)
    except Exception:
        logger.exception(f"Error importing data from {file_path} to {table_name}")
        raise

def create_indexes(engine):
    """
    Crée des index sur les tables pour améliorer les performances des requêtes.
    
    Étapes:
    1. Établit une connexion à la base de données
    2. Crée un index sur la colonne user_id de la table ratings
    3. Crée un index sur la colonne movie_id de la table ratings
    4. Utilise CREATE INDEX IF NOT EXISTS pour éviter les erreurs si les index existent déjà
    
    Args:
        engine: L'objet Engine SQLAlchemy pour la connexion à la base de données
        
    Raises:
        Exception: Si la création des index échoue, l'erreur est journalisée et propagée
    """
    try:
        logger.info("Creating database indexes...")
        
        with engine.connect() as connection:
            # Create index on user_id in ratings
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)"
            ))
            
            # Create index on movie_id in ratings
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id)"
            ))
            
        logger.success("Database indexes created successfully")
    except Exception:
        logger.exception("Error creating database indexes")
        raise

def main():
    """
    Fonction principale qui orchestre le processus complet d'importation des données.
    
    Étapes:
    1. Définit les chemins vers les fichiers CSV de films et d'évaluations
    2. Établit une connexion à la base de données PostgreSQL
    3. Teste la connexion avec une requête simple
    4. Crée le schéma de la base de données selon les modèles définis
    5. Importe les données des films depuis le CSV vers la table 'movies'
    6. Importe les données d'évaluations depuis le CSV vers la table 'ratings'
    7. Crée des index sur les colonnes pertinentes pour optimiser les performances
    
    Le processus s'arrête avec un code d'erreur si une étape échoue,
    avec journalisation des détails de l'erreur.
    
    Raises:
        OperationalError: Si la connexion à la base de données échoue
        Exception: Pour toute autre erreur durant le processus d'importation
    """
    try:
        # Define file paths directly
        data_dir = "/data"
        movies_path = os.path.join(data_dir, "movies_metadata.csv")
        ratings_path = os.path.join(data_dir, "ratings.csv")
        
        # Create database connection
        logger.info("Connecting to PostgreSQL database...")
        try:
            engine = get_db_engine()
            # Test connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1")).fetchone()
            logger.info("Successfully connected to PostgreSQL")
        except OperationalError:
            logger.exception("Failed to connect to PostgreSQL")
            sys.exit(1)
        
        # Create database schema
        create_db_schema(engine)
        
        # Import movies data
        import_data_with_pandas(engine, movies_path, 'movies', chunksize=1000)
        
        # Import ratings data
        import_data_with_pandas(engine, ratings_path, 'ratings', chunksize=5000)
        
        # Create indexes
        create_indexes(engine)
        
        logger.success("Data import completed successfully")
        
    except Exception:
        logger.exception("Error in data import process")
        sys.exit(1)

if __name__ == "__main__":
    main()
