from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel


class OTPVerificationResponse(BaseModel):
    phone_number: str
    otp_code: str
class OTPVerificationRequest(BaseModel):
    phone_number: str
    otp_code: str
class UpdatePassword(BaseModel):
    phone_number: str
    new_password: str
    
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
    phone_number = Column(Integer, index=True)

    forgot_passwords = relationship("ForgotPassword", back_populates="user")

class ForgotPassword(Base):
    __tablename__ = "FORGOT_PASSWORD"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255))
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("USERS.id"))
    phone_number = Column(Integer, index=True)
    hashed_otp = Column(String(64))

    user = relationship("USERS", back_populates="forgot_passwords")




class OTPVerification(Base):  # Renamed to avoid naming collision
    __tablename__ = "OTP_VERIFICATION_REQUEST"

    id = Column(Integer, primary_key=True, index=True)
    phone_number =  Column(Integer, index=True)
    otp_code =  Column(Integer, index=True)
    created_at = Column(DateTime)
