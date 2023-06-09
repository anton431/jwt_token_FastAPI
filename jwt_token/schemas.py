from pydantic import BaseModel
from datetime import date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    salary: int | None = None
    promotion: date | None = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True