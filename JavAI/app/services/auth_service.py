from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from jose import jwt, JWTError


def user_login(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return False

    payload_data = {
        "id": user.id
    }

    access_token = create_access_token(payload_data)
    refresh_token = create_refresh_token(payload_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key_refresh,
            algorithms=[settings.algorithm]
        )

        user_id: int = payload.get("id")
        if user_id is None:
            return None

        return create_access_token({"id": user_id})
    except JWTError:
        return False


