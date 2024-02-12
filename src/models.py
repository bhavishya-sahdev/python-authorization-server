from uuid import uuid4
from sqlalchemy import Column, String, UUID, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, default=uuid4, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)