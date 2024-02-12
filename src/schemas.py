# Holds pydantic models
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID

    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True