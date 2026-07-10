from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr  # Έλεγχος αν είναι πραγματικό email
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)
