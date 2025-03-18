#!/usr/bin/env python3
import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from loguru import logger

# Import SQLAlchemy models
from models import Base, Movie, Rating

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("/data/import_data.log", rotation="10 MB", level="INFO")

def check_csv_files():
    """Check if the required CSV files exist in the data directory."""
    data_dir = "/data"
    movies_path = os.path.join(data_dir, "movies_metadata.csv")
    ratings_path = os.path.join(data_dir, "ratings.csv")
    
    # Check if both files exist
    if not os.path.exists(movies_path):
        logger.error(f"Movies CSV file not found at {movies_path}")
        return None, None
    
    if not os.path.exists(ratings_path):
        logger.error(f"Ratings CSV file not found at {ratings_path}")
        return None, None
    
    logger.info(f"Found CSV files: {movies_path} and {ratings_path}")
    return movies_path, ratings_path

def get_db_engine():
    """Create SQLAlchemy engine for PostgreSQL."""
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = "postgres"  # Docker service name
    port = os.environ.get("POSTGRES_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "movies")
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(db_url)

def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    engine = get_db_engine()
    retries = 30
    
    logger.info("Waiting for PostgreSQL to be ready...")
    
    for i in range(retries):
        try:
            # Try to connect to PostgreSQL
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("PostgreSQL is ready!")
            return engine
        except OperationalError:
            logger.info(f"PostgreSQL not ready yet (attempt {i+1}/{retries}). Retrying in 2 seconds...")
            time.sleep(2)
    
    logger.error("Could not connect to PostgreSQL after multiple attempts")
    return None

def create_db_schema(engine):
    """Create database schema using SQLAlchemy models."""
    try:
        logger.info("Creating database schema...")
        Base.metadata.create_all(engine)
        logger.success("Database schema created successfully")
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        raise

def import_movies(engine, movies_path):
    """Import movies data into PostgreSQL using SQLAlchemy."""
    try:
        logger.info(f"Importing movies data from {movies_path}")
        
        # Read movies CSV
        movies_df = pd.read_csv(movies_path)
        logger.info(f"Found {len(movies_df)} movies in CSV file")
        
        # Rename columns to match SQLAlchemy model if necessary
        if 'movieId' in movies_df.columns:
            movies_df = movies_df.rename(columns={
                'movieId': 'movie_id'
            })
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Use SQLAlchemy Core for bulk insert for better performance
            # Create a list of dictionaries for bulk insert
            movies_data = movies_df.to_dict(orient='records')
            
            # Insert in batches
            batch_size = 1000
            for i in range(0, len(movies_data), batch_size):
                batch = movies_data[i:i + batch_size]
                logger.info(f"Importing movies batch {i//batch_size + 1} of {(len(movies_data) + batch_size - 1)//batch_size}")
                
                # Insert with conflict resolution
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                        INSERT INTO movies (movie_id, title, genres)
                        VALUES (:movie_id, :title, :genres)
                        ON CONFLICT (movie_id) DO NOTHING
                        """),
                        batch
                    )
            
            session.commit()
            logger.success(f"Imported {len(movies_df)} movies")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error importing movies data: {e}")
        raise

def import_ratings(engine, ratings_path):
    """Import ratings data into PostgreSQL using SQLAlchemy."""
    try:
        logger.info(f"Importing ratings data from {ratings_path}")
        
        # Read ratings CSV
        ratings_df = pd.read_csv(ratings_path)
        logger.info(f"Found {len(ratings_df)} ratings in CSV file")
        
        # Rename columns to match SQLAlchemy model if necessary
        if 'userId' in ratings_df.columns and 'movieId' in ratings_df.columns:
            ratings_df = ratings_df.rename(columns={
                'userId': 'user_id',
                'movieId': 'movie_id'
            })
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Use SQLAlchemy Core for bulk insert for better performance
            # Create a list of dictionaries for bulk insert
            ratings_data = ratings_df.to_dict(orient='records')
            
            # Insert in batches
            batch_size = 5000
            for i in range(0, len(ratings_data), batch_size):
                batch = ratings_data[i:i + batch_size]
                logger.info(f"Importing ratings batch {i//batch_size + 1} of {(len(ratings_data) + batch_size - 1)//batch_size}")
                
                # Insert with conflict resolution
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                        INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                        VALUES (:user_id, :movie_id, :rating, :timestamp)
                        ON CONFLICT (user_id, movie_id) DO NOTHING
                        """),
                        batch
                    )
            
            session.commit()
            logger.success(f"Imported {len(ratings_df)} ratings")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"Error importing ratings data: {e}")
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
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")
        raise

def main():
    """Main function to orchestrate the data import process."""
    try:
        # Check if CSV files exist
        movies_path, ratings_path = check_csv_files()
        if not movies_path or not ratings_path:
            logger.error("Required CSV files not found. Please place movies.csv and ratings.csv in the data directory.")
            sys.exit(1)
        
        # Wait for PostgreSQL to be ready
        engine = wait_for_postgres()
        if not engine:
            sys.exit(1)
        
        # Create database schema
        create_db_schema(engine)
        
        # Import data into PostgreSQL
        import_movies(engine, movies_path)
        import_ratings(engine, ratings_path)
        
        # Create indexes
        create_indexes(engine)
        
        logger.success("Data import completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data import process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
