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
    """Create SQLAlchemy engine for PostgreSQL."""
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = "postgres"  # Docker service name
    port = os.environ.get("POSTGRES_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "movies")
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(db_url)

def create_db_schema(engine):
    """Create database schema using SQLAlchemy models."""
    try:
        logger.info("Creating database schema...")
        Base.metadata.create_all(engine)
        logger.success("Database schema created successfully")
    except Exception:
        logger.exception("Error creating database schema")
        raise

def import_data_with_pandas(engine, file_path, table_name, chunksize):
    """Import data from a single CSV file into PostgreSQL using pandas."""
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
    """Create indexes for better performance."""
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
    """Main function to orchestrate the data import process."""
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
