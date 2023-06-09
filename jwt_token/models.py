from sqlalchemy import Column, DateTime, Float, Integer, String, DATE
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    hashed_password = Column(String)
    salary = Column(Integer)
    promotion = Column(DATE)


