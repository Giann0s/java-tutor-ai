from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.models.user import User


def user_login(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False

    payload_data = {
        "id": user.id
    }
    return create_access_token(payload_data)

