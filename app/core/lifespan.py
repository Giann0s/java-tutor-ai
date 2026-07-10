from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import models
from app.core.startup import create_first_admin
from app.db.database import Base, engine, SessionLocal


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_first_admin(db)
    finally:
        db.close()

    yield
