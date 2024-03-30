from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

class USERS(Base):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, index=True)

    forgot_passwords = relationship("ForgotPassword", back_populates="user")

    # todos = relationship("Todos", back_populates="owner")

class ForgotPassword(Base):
    __tablename__ = "FORGOT_PASSWORD"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255))
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("USERS.id"))

    user = relationship("USERS", back_populates="forgot_passwords")

# class Todos(Base):
#     __tablename__ = "todos"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     priority = Column(Integer, index=True)
#     complete = Column(Boolean, default=False)
#     owner_id = Column(Integer, ForeignKey("USERS.id"))

#     owner = relationship("USERS", back_populates="todos")