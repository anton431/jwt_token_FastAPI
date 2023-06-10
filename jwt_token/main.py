from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uvicorn

from settings import engine, ACCESS_TOKEN_EXPIRE_MINUTES
import schemas
import models
import crud


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(crud.get_db)):
    """
    Get a custom token from the database using username from
    the form field. If there is no such user, return the error
    message "incorrect username or password".
    """
    user = crud.authenticate_user(db=db, username=form_data.username,
                                  password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
        current_user: Annotated[schemas.User,
                                Depends(crud.get_current_user)]):
    """
    Get the data of an authorized user
    """
    return current_user


@app.post("/users/", response_model=schemas.User)
async def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(crud.get_db)):
    """
    Creating a user by name and password
    """
    db_user = crud.get_user(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400,detail="User already registered")

    return crud.create_user(db=db, user=user)
