from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
import os

# Define the path to the SQLite database
DATABASE_URL = "sqlite:///./data/news_database.db"

# Create the data directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE_URL[10:]), exist_ok=True)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the FastAPI app
app = FastAPI()

# Define the Pydantic model for the response
class ArticleCount(BaseModel):
    date: str
    count: int

# Pydantic model for input data
class Article(BaseModel):
    url: str
    title: str
    label: str
    theme: str
    badge: str
    datetime: str
    author: str
    text: str


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to count articles per day
@app.get("/count/day", response_model=List[ArticleCount])
def count_articles_per_day(db: Session = Depends(get_db)):
    query = text("""
        SELECT DATE(datetime) as date, COUNT(*) as count
        FROM Articles
        GROUP BY DATE(datetime)
        ORDER BY DATE(datetime);
    """)
    try:
        result = db.execute(query).fetchall()
        # Access elements using integer indices instead of strings to avoid the tuple error
        counts = [{"date": row[0], "count": row[1]} for row in result]
        return counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/articles/")
def add_articles(articles: List[Article], db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO Articles (url, title, label, theme, badge, datetime, author, text)
            VALUES (:url, :title, :label, :theme, :badge, :datetime, :author, :text)
            ON CONFLICT(url) DO NOTHING
        """)  # ✅ Add ON CONFLICT to avoid duplicates

        for article in articles:
            db.execute(
                query,
                {
                    "url": article.url or None,
                    "title": article.title or None,
                    "label": article.label or None,
                    "theme": article.theme or None,
                    "badge": article.badge or None,
                    "datetime": article.datetime or None,
                    "author": article.author or None,
                    "text": article.text or None
                }
            )

        db.commit()
        return {"status": "success", "message": f"{len(articles)} articles processed"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
