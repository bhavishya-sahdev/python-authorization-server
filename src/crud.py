from sqlalchemy import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, Body
from datetime import datetime, timedelta
import bcrypt
import models, schemas
import jwt
import os

JWT_SECRET = os.environ.get("JWT_SECRET")

def get_user(db:Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    queried_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not queried_user is None:
        raise HTTPException(status_code=400, detail="User already exists")

    bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(bytes, salt)

    now = datetime.now()
    db_user = models.User(email=user.email, hashed_password=hashed_password.decode('utf-8'), created_at=now, updated_at=now)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = generate_authentication_token(db_user.email, str(db_user.id))
    return token

def get_user_by_email_password(db: Session, user: schemas.UserCreate):
    db_user = get_user_by_email(db, user.email)

    if not db_user is None:
        bytes = user.password.encode('utf-8')
        db_bytes = db_user.hashed_password.encode('utf-8')
        if bcrypt.checkpw(bytes, db_bytes):
            return generate_authentication_token(db_user.email, str(db_user.id))

    raise HTTPException(status_code=400, detail="User not found")

def generate_authentication_token(email, id):
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "email": email,
        "id": id,
        "exp": expiration_time
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print(verify_authentication_token(encoded_jwt))
    return encoded_jwt

def verify_authentication_token(token: str = Body(embed=True)):
    try:
        decoded_jwt = jwt.decode(token, JWT_SECRET, algorithms="HS256")
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        print("here")
        raise HTTPException(status_code=400,detail="Token expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=400,detail="Token invalid")
    except:
        raise HTTPException(status_code=500,detail="Unknown error occured")

def refresh_authentication_token(token: str):
    payload = verify_authentication_token(token)
    if payload:
        new_token = generate_authentication_token(payload['email'], payload['id'])
        return new_token
    else:
        raise HTTPException(status_code=500,detail="Failed to refresh authentication token")
