import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, logger, status, Request, Response,Form
# from fastapi import FastAPI, JSONResponse
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
from fastapi.responses import HTMLResponse, JSONResponse  
from fastapi.templating import Jinja2Templates
from models import ForgotPassword
import random
from fastapi.params import Body
from typing import Dict,Any,List
import logging



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
 
       
async def get_form_data(request: Request) -> dict:
    try:
        form_data = await request.json()
        email = form_data.get("email")
        password = form_data.get("password")
        if email is None or password is None:
            raise HTTPException(status_code=400, detail="Missing email or password")
        return {
            "email": email,
            "password": password
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")


def authenticate_user(email: str, password: str, db):
    USERS = db.query(models.USERS)\
        .filter(models.USERS.email == email)\
        .first()
    if not USERS:
        return False  # User not found
    if not verify_password(password, USERS.hashed_password):
        return None  # Incorrect password
    return USERS  # User authenticated


logger = logging.getLogger(__name__)

@router.post("/token")
async def login_for_access_token(response: Response, form_data: dict = Depends(get_form_data), db: Session = Depends(get_db)):
    email = form_data.get("email")
    password = form_data.get("password")
    logger.debug(f"Received email: {email}")  # Correct usage of logger
    USERS = authenticate_user(email, password, db)
    if USERS is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    if USERS is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")

    token_expires = timedelta(minutes=60)
    token = create_access_token(USERS.email, USERS.id, expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}





@router.get("/logout")
async def logout(request: Request):
    try:
        response = RedirectResponse(url="https://www.austinpartnership.in", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        return JSONResponse(content={"message": "Logout Successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "Logout Failed"}, status_code=500)


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
    

@router.post("/test")
async def test_endpoint(request: Request):
    try:
        form_data = await request.json()
        return {"received": form_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")

