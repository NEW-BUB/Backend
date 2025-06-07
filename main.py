from typing import List

from fastapi import FastAPI
from fastapi import APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.middleware.cors import CORSMiddleware

from app.database import engineconn
from app import models
from app.models import *
from app.routers import keywords, news, laws, parties
from app.services.party_service import PartyService

app = FastAPI(title = "NEWBUB")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

engine = engineconn()

models.Base.metadata.create_all(bind=engine.engine)

session = engine.sessionmaker()

app.include_router(keywords.router)
app.include_router(news.router)
app.include_router(laws.router)
app.include_router(parties.router)


# uvicorn main:app --reload --host=0.0.0.0 --port=8000
