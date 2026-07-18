from pydantic import BaseModel, EmailStr
from fastapi import Body

class LoginRequest(BaseModel):
    email: EmailStr = Body()
    password: str = Body()
    
class CreateUserRequest(BaseModel):
    first_name: str = Body()
    last_name: str = Body()
    email: EmailStr = Body()
    password: str = Body()
    
class UserResponse(BaseModel):
    id: int 
    first_name: str
    last_name: str
    email: EmailStr