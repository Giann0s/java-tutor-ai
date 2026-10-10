from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.dependencies import db_dependency
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/login")
async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token = auth_service.user_login(db, form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Λάθος στοιχεία."
        )

    return {"access_token": token, "token_type": "bearer"}