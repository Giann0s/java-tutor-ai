from fastapi import FastAPI

from app.api.routers import auth_router, user_router, chat_router, topic_router
from app.core.lifespan import app_lifespan


app = FastAPI(lifespan=app_lifespan)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(topic_router.router)
