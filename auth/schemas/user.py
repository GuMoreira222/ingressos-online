from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from models.user import RoleEnum

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER

class UserRead(UserBase):
    id: int
    role: RoleEnum
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
