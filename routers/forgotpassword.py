import sys

sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response,Form
# from fastapi import FastAPI, JSONResponse
from pydantic import BaseModel
from models import USERS,ForgotPassword
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse  
from fastapi.templating import Jinja2Templates
import requests,hashlib,random
from typing import Dict,Any,List
from routers.otp import send_otp_to_mobile
from sqlalchemy import desc

router = APIRouter(
    prefix="/forgot",
    tags=["forgot"],
    responses={401: {"user": "Not authorized"}}
)

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"


SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"
API_KEY = "Lz9ApKcGqcFQRtHk9luQFMSOA8munwdd1ux9JjFEv9VHXJquokooJFt33s86"  # Replace this with your Fast2SMS API key

otp_storage = {}


templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_password_hash(password):
    # Implement password hashing logic here (e.g., using bcrypt)
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    # Implement password verification logic here (e.g., using bcrypt)
    return bcrypt_context.verify(plain_password, hashed_password)

class OTPVerificationRequest(BaseModel):
    phone_number: str
    otp_code: str

def generate_otp_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_to_mobile(phone_number: str, otp_code: str):
    querystring = {"authorization": API_KEY, "variables_values": otp_code, "route": "otp", "numbers": phone_number}
    headers = {
        'cache-control': "no-cache"
    }
    response = requests.get(SMS_API_URL, headers=headers, params=querystring)
    response_data = response.json()
    if response_data.get('return'):
        return response_data
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP")


@router.post("/send_otp")
async def send_otp(request: Request, phone_number: str):
    try:
        otp_code = generate_otp_code()
        otp_storage[phone_number] = otp_code
        send_otp_to_mobile(phone_number, otp_code)
        return {"message": "OTP code sent to your mobile phone"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @router.post("/forgot_password")
# async def forgot_password(request: Request, email: str,phone_number: str, db: Session = Depends(get_db)):
#     try:
#         user = db.query(USERS).filter(USERS.email == email,USERS.phone_number == phone_number).first()
#         if user:
#             otp_code = generate_otp_code()  # Generate random 6-digit OTP
#             # send_otp_to_mobile(phone_number, otp_code)  # Automatically send OTP
#             # return {"message": "OTP code sent to your mobile phone"}
#             return {"message": "OTP code generated", "otp_code": otp_code}
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.post("/forgot_password")
# async def forgot_password(request: Request, email: str, phone_number: str, db: Session = Depends(get_db)):
#     try:
#         user = db.query(USERS).filter(USERS.email == email, USERS.phone_number == phone_number).first()
#         if user:
#             otp_code = generate_otp_code()  # Generate random 6-digit OTP
#             otp_code = hashlib.sha256(otp_code.encode()).hexdigest()  # Hash the OTP
#             forgot_password_instance = ForgotPassword(phone_number=phone_number, hashed_otp=otp_code)
#             db.add(forgot_password_instance)
#             db.commit()
#             # send_otp_to_mobile(phone_number, otp_code)  # Automatically send OTP
#             # return {"message": "OTP code sent to your mobile phone"}
#             return {"message": "OTP code generated", "otp_code": otp_code}
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def __init__(self, email: str, created_at: datetime, user_id: int, phone_number: str, hashed_otp: str):
        self.email = email
        self.created_at = created_at
        self.user_id = user_id
        self.phone_number = phone_number
        self.hashed_otp = hashed_otp

@router.post("/forgot_password")
async def forgot_password(request: Request, email: str, phone_number: str, db: Session = Depends(get_db)):
    try:
        user = db.query(USERS).filter(USERS.email == email, USERS.phone_number == phone_number).first()
        if user:
            otp_plain = generate_otp_code()  # Generate random 6-digit OTP
            otp_code = hashlib.sha256(otp_plain.encode()).hexdigest()  # Hash the OTP
            created_at = datetime.now()
            # Store the hashed OTP code in the database
            forgot_password_instance = ForgotPassword(email=email, created_at=created_at, user_id=user.id, phone_number=phone_number, hashed_otp=otp_code)
            db.add(forgot_password_instance)
            db.commit()
            # send_otp_to_mobile(phone_number, otp_code)  # Automatically send OTP
            # return {"message": "OTP code sent to your mobile phone"}
            return {"message": "OTP code generated", "otp_code": otp_plain}  # Return success message without exposing the OTP code
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    

@router.post("/verify_otp", response_model=None)
async def verify_otp(request: Request, phone_number: str, otp_code: str, db: Session = Depends(get_db)):
    try:
        # Retrieve the latest entry for the given phone number
        forgot_password_entry = db.query(ForgotPassword).filter(ForgotPassword.phone_number == phone_number).order_by(desc(ForgotPassword.id)).first()
        
        if forgot_password_entry:
            stored_hashed_otp = forgot_password_entry.hashed_otp

            # Hash the submitted OTP and compare with the stored hashed OTP
            submitted_hashed_otp = hashlib.sha256(otp_code.encode()).hexdigest()
            if submitted_hashed_otp == stored_hashed_otp:
                # OTP code verified successfully, no need to delete entry
                return {"message": "OTP code verified successfully"}
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP code")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No OTP entry found for this phone number")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    

@router.post("/update_password", response_model=Dict[str, str])
async def update_password(email: str,phone_number: str, new_password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(USERS).filter(USERS.phone_number == phone_number, USERS.email == USERS.email).first()
        if user:
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            db.commit()

            # Return the response body
            return {"phone_number": phone_number, "new_password": new_password}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

