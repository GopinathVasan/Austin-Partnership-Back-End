import requests
import random
from fastapi import APIRouter, Depends, HTTPException, status, Request
from database import SessionLocal
from typing import Dict
from models import OTPVerificationRequest, OTPVerificationResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/otp",
    tags=["otp"],
    responses={401: {"user": "Not authorized"}}
)

SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"
API_KEY = "Lz9ApKcGqcFQRtHk9luQFMSOA8munwdd1ux9JjFEv9VHXJquokooJFt33s86"  # Replace this with your Fast2SMS API key

otp_storage = {}

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

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

@router.post("/verify_otp", response_model=None)
async def verify_otp(request: Request, otp_verification_request: OTPVerificationRequest, db: Session = Depends(get_db)):
    try:
        phone_number = otp_verification_request.phone_number
        submitted_otp = otp_verification_request.otp_code
        stored_otp = otp_storage.get(phone_number)
        if stored_otp and stored_otp == submitted_otp:
            del otp_storage[phone_number]  # Clear OTP from memory after verification
            return {"message": "OTP code verified successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP code")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))