# backend/routers/news.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.news import NewsCreate, NewsResponse
from backend.services import crud  # ✅ import the single CRUD module

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/", response_model=List[NewsResponse])
def read_news(db: Session = Depends(get_db)):
    return crud.get_all_news(db)  # call directly from crud

@router.post("/", response_model=NewsResponse)
def add_news(news: NewsCreate, db: Session = Depends(get_db)):
    return crud.create_news(db, news)  # call directly from crud