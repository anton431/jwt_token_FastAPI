from datetime import datetime, timedelta
from typing import Annotated, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from schemas import User, TokenData, UserCreate
from settings import SECRET_KEY, ALGORITHM, SessionLocal
import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    """
    Check whether the received password matches the saved hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash the password coming from the user.
    """
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    """
    Get the current user.
    """
    user = db.query(models.UserDB).filter(
        models.UserDB.username == username).first()
    if user:
        return user


def create_user(db: Session, user: UserCreate):
    """
    Create a new user by name and password.
    """
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.UserDB(username=user.username,
                            hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate and return the user.
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    """
    Creating a token with an expiration time of 5 minutes.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)):
    """
    Get the JWT tokens, Decrypt the received token, verify it,
    and return the current user. If the token is invalid, return
    an HTTP error immediately.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user
