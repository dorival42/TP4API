from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    
    movie_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    genres = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<Movie(movie_id={self.movie_id}, title='{self.title}')>"

class Rating(Base):
    __tablename__ = 'ratings'
    
    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), primary_key=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(BigInteger)
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"
