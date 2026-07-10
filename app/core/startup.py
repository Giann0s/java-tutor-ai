from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.core.config import settings


# Αν δεν υπάρχει admin δημιουργείται ο πρώτος
def create_first_admin(db: Session):
    admin = db.query(User).filter(User.role == "admin").first()

    if not admin:
        first_admin = User(
            email=settings.admin_email,
            first_name="Admin",
            last_name="",
            hashed_password=hash_password(settings.admin_password),
            role="admin",
            is_active=True
        )

        db.add(first_admin)
        db.commit()
