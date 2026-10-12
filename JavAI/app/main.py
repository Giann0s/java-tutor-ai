from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routers import auth_router, user_router, chat_router, topic_router, exercise_router, statistics_router
from app.core.lifespan import app_lifespan


app = FastAPI(lifespan=app_lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(topic_router.router)
app.include_router(exercise_router.router)
app.include_router(statistics_router.router)