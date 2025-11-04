from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.news import NewsItem

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.get("/news/test")
def test_news(db: Session = Depends(get_db)):
    try:
        one_news = db.query(NewsItem).first()
        return {
            "status": "ok",
            "news": one_news.title if one_news else "No news found"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
