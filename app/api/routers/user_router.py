from fastapi import APIRouter, HTTPException, Path
from starlette import status

from app.api.dependencies import db_dependency, admin_dependency, user_dependency
from app.services import user_service
from app.schemas.user_schemas import CreateUser, UserResponse, UpdateUser, UpdatePassword

router = APIRouter(
    prefix="/users",
    tags=['user']
)


@router.post("/register/student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_student(db: db_dependency, new_student: CreateUser):
    created_student = user_service.register_user(db, new_student, role="student")
    if not created_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Αυτό το email χρησιμοποιείται ήδη."
        )
    return created_student


@router.post("/register/professor", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_professor(db: db_dependency, new_professor: CreateUser, admin: admin_dependency):
    created_professor = user_service.register_user(db, new_professor, role="professor")
    if not created_professor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Αυτό το email χρησιμοποιείται ήδη."
        )
    return created_professor


@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(db: db_dependency, new_admin: CreateUser, admin: admin_dependency):
    created_admin = user_service.register_user(db, new_admin, role="admin")
    if not created_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Αυτό το email χρησιμοποιείται ήδη."
        )
    return created_admin


@router.get("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency):
    return user


@router.patch("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user_info(user: user_dependency, updated_info: UpdateUser, db: db_dependency):
    updated_user = user_service.update_user_info(user, updated_info, db)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Αυτό το email χρησιμοποιείται ήδη."
        )
    return updated_user


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def admin_user_update(db: db_dependency, admin: admin_dependency, updated_info: UpdateUser,
                            user_id: int = Path(gt=0)):
    target_user = user_service.get_user_by_id(db, user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ο χρήστης δεν βρέθηκε."
        )
    updated_user = user_service.update_user_info(target_user, updated_info, db)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Αυτό το email χρησιμοποιείται ήδη."
        )
    return updated_user


@router.patch("/profile/password", status_code=status.HTTP_200_OK)
async def update_password(db: db_dependency, user: user_dependency, password_data: UpdatePassword):
    updated_user = user_service.update_user_password(db, user, password_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Λάθος κωδικός."
        )
    return {"message": "Ο κωδικός ενημερώθηκε επιτυχώς."}


# Soft delete τον user, δηλαδή αλλαγή του is_active σε False
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(db: db_dependency, user: user_dependency):
    user_service.soft_delete_user(db, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_soft_delete_user(db: db_dependency, admin: admin_dependency, user_id: int = Path(gt=0)):
    target_user = user_service.get_user_by_id(db, user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ο χρήστης δεν βρέθηκε."
        )
    user_service.soft_delete_user(db, target_user)
