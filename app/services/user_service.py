from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.schemas.user_schemas import CreateUser, UpdateUser, UpdatePassword


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, new_user: CreateUser, role: str):
    existing_user = db.query(User).filter(User.email == new_user.email).first()
    if existing_user:
        return False

    new_user_model = User(
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        hashed_password=hash_password(new_user.password),
        role=role,
        is_active=True
    )
    db.add(new_user_model)
    db.commit()
    db.refresh(new_user_model)
    return new_user_model


def update_user_info(user: User, updated_info: UpdateUser, db: Session):
    if updated_info.email is not None:
        existing_user = db.query(User).filter(User.email == updated_info.email, User.id != user.id).first()
        if existing_user:
            return False

    update_dict = updated_info.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: User, password_data: UpdatePassword):
    correct_password = verify_password(password_data.current_password, user.hashed_password)
    if not correct_password:
        return False
    updated_password = hash_password(password_data.new_password)
    user.hashed_password = updated_password
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()



