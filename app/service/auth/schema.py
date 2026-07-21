from pydantic import BaseModel, EmailStr, ConfigDict
from fastapi import Body


class LoginRequest(BaseModel):
    email: EmailStr = Body()
    password: str = Body()


class UserBase(BaseModel):
    first_name: str = Body()
    last_name: str = Body()
    email: EmailStr = Body()


class CreateUserRequest(UserBase):
    password: str = Body()


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Token(BaseModel):
    access_token: str
    token_type: str
