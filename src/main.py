from fastapi import Depends, FastAPI, HTTPException, Body
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()

import crud, models, schemas
from database import SessionLocal, engine, Base

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/register")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return {"token": crud.create_user(db, user)}


@app.post("/users/user", response_model=schemas.User)
def read_user(user: dict = Depends(crud.verify_authentication_token), db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user.get('id'))
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/login")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    token = crud.get_user_by_email_password(db, user)
    if token is None:
        raise HTTPException(status_code=400, detail="Incorrect input")
    return token

@app.post("/users/token/refresh")
def refresh_token(token: str = Body(embed=True)):
    if token is None:
        raise HTTPException(400, detail="No token provided")

    token = crud.refresh_authentication_token(token)
    return token
