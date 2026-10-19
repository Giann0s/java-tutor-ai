from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.dependencies import db_dependency
from app.schemas.auth_schemas import RefreshTokenRequest
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


@router.post("/login")
async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    tokens = auth_service.user_login(db, form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Λάθος στοιχεία."
        )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    new_access_token = auth_service.refresh_access_token(request.refresh_token)
    if new_access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Μη έγκυρο refresh token."
        )
    if new_access_token is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Το refresh token έχει λήξει ή είναι άκυρο. Παρακαλώ συνδεθείτε ξανά."
        )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
