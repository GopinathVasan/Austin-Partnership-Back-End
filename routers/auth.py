import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response,Form
from pydantic import BaseModel
from typing import Optional
import models
from starlette.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse  
from fastapi.templating import Jinja2Templates
from models import ForgotPassword
import random
from fastapi.params import Body
from typing import Dict,Any,List



router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


class LoginForm(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
    phone_number: str

class OTPRequest(BaseModel):
    email: str
    otp_code: str


class UpdatePassword(BaseModel):
    token: str
    password: str
    confirmPassword: str

def send_otp_to_mobile(phone_number: str, otp_code: str):
    # Placeholder function to simulate sending OTP to a mobile phone
    print(f"Sending OTP code {otp_code} to {phone_number}")




def generate_otp_code():
    # Generate a random 6-digit OTP code
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


# async def get_form_data(request: Request) -> dict:
#     form_data = request.json()
#     return form_data
    # form_data = await request.form()
    # return dict(form_data)

# def get_form_data(request: Request) -> dict:
#     form_data = request.json()
#     return form_data

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")
    

# async def get_form_data(request: Request) -> dict:
#     form_data = await request.form()
#     return {key: value for key, value in form_data.items()}
       
async def get_form_data(request: Request) -> dict:
    form_data = await request.json()
    return {
        "email": form_data.get("email").encode(),
        "password": form_data.get("password").encode()
    }

def authenticate_user(email: str, password: str, db):
    USERS = db.query(models.USERS)\
        .filter(models.USERS.email == email)\
        .first()
    if not USERS:
        return False  # User not found
    if not verify_password(password, USERS.hashed_password):
        return None  # Incorrect password
    return USERS  # User authenticated


@router.post("/token")
async def login_for_access_token(response: Response, form_data: dict = Depends(get_form_data), db: Session = Depends(get_db)):
    email = form_data.get("email")
    password = form_data.get("password")
    USERS = authenticate_user(email, password, db)
    if USERS is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    if USERS is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")

    token_expires = timedelta(minutes=60)
    token = create_access_token(USERS.email, USERS.id, expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}



# Modify the authenticate_user function to accept the decorator



# @router.post("/token")
# async def login_for_access_token(form_data: LoginForm = Depends(get_form_data), db: Session = Depends(get_db)):
#     user = authenticate_user(form_data.username, form_data.password, db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect")
#     token_expires = timedelta(minutes=60)
#     token = create_access_token(user.username, user.id, expires_delta=token_expires)
#     return {"access_token": token, "token_type": "bearer"}


# @router.post("/token")
# async def login_for_access_token(response: Response, request: Request, db: Session = Depends(get_db)):
#     form_data_dict = await get_form_data(request)
#     user = await authenticate_user(form_data_dict['email'], form_data_dict['password'], db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
#     token_expires = timedelta(minutes=60)
#     token = create_access_token(user.email, user.id, expires_delta=token_expires)
#     response.set_cookie(key="access_token", value=token, httponly=True)
#     return {"access_token": token, "token_type": "bearer"}
    
# @router.post("/token")
# async def login_for_access_token(response: Response, request: Request, db: Session = Depends(get_db)):
#     form_data = await get_form_data(request)
#     user = await authenticate_user(form_data.get('email'), form_data.get('password'), db)
#     if not user:
#         raise HTTPException(status_code=401, detail="Email or password is incorrect")
#     token_expires = timedelta(minutes=60)
#     token = create_access_token(user.email, user.id, expires_delta=token_expires)
#     response.set_cookie(key="access_token", value=token, httponly=True)
#     return {"access_token": token, "token_type": "bearer"}






#  @router.post("/token")
# async def login_for_access_token(response: Response, form_data: LoginForm = Depends(), db: Session = Depends(get_db)):
#     # Check if the provided email exists in the database
#     user = db.query(models.USERS).filter(models.USERS.email == form_data.email).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    
#     # Verify the password for the user
#     if not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")

#     # Generate and return the access token if the user is authenticated
#     token_expires = timedelta(minutes=60)
#     token = create_access_token(user.email, user.id, expires_delta=token_expires)
#     response.set_cookie(key="access_token", value=token, httponly=True)
#     return {"access_token": token, "token_type": "bearer"}


@router.get("/logout")
async def logout(request: Request):
    try:
        response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        msg = "Logout Successfully"
        return response
    except Exception as e:
        msg = "Logout Failed"
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/register")
async def register_user(request: Request, user_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    email = user_data.get("email")
    username = user_data.get("username")
    firstname = user_data.get("firstname")
    lastname = user_data.get("lastname")
    phonenumber = user_data.get("phonenumber")
    password = user_data.get("password")
    confirmPassword = user_data.get("confirmPassword")

    validation1 = db.query(models.USERS).filter(models.USERS.username == username).first()
    validation2 = db.query(models.USERS).filter(models.USERS.email == email).first()

    if password != confirmPassword or validation1 is not None or validation2 is not None:
        raise HTTPException(status_code=400, detail="Invalid registration request")

    user_model = models.USERS()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.phone_number = phonenumber

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    try:
        db.add(user_model)
        db.commit()
        return {"message": "User successfully created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
# Ensure proper dependency injection for the database session
@router.post("/forgot_password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = request.email
        phone_number = request.phone_number
        user = db.query(models.USERS).filter(models.USERS.email == email, models.USERS.phone_number == phone_number).first()
        if user:
            otp_code = generate_otp_code()
            forgot_password_instance = ForgotPassword(email=email, user_id=user.id, otp_code=otp_code, phone_number=phone_number)
            db.add(forgot_password_instance)
            db.commit()
            send_otp_to_mobile(phone_number, otp_code)
            return {"message": "OTP code sent to your mobile phone"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email or phone number not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/verify_otp")
async def verify_otp(request: OTPRequest, db: Session = Depends(get_db)):
    try:
        email = request.email
        otp_code = request.otp_code
        forgot_password_instance = db.query(models.ForgotPassword).filter_by(email=email, otp_code=otp_code).first()
        if forgot_password_instance:
            # OTP code is valid
            db.delete(forgot_password_instance)
            db.commit()
            return {"message": "OTP code verified successfully"}
        else:
            # OTP code is invalid
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP code")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/update_password", response_class=HTMLResponse)
async def update_password(response: Response, form_data: UpdatePassword, db: Session = Depends(get_db)):
    try:
        # You need to define `password` and `confirmPassword` from `form_data`
        password = form_data.password
        confirmPassword = form_data.confirmPassword
        if password == confirmPassword:
            user = db.query(models.USERS).filter(models.USERS.token == form_data.token).first()
            if user:
                hash_password = get_password_hash(form_data.password)
                user.hashed_password = hash_password
                db.commit()
                msg = "Password successfully updated"
            else:
                msg = "Invalid token"
        else:
            msg = "Passwords do not match"
        # return templates.TemplateResponse("update_password.html", {"request": request, "msg": msg})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))