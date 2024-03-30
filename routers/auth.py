import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
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
from fastapi import Request
from fastapi.templating import Jinja2Templates

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

def authenticate_user(username: str, password: str, db):
    user = db.query(models.USERS).filter(models.USERS.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

class ForgotPassword(BaseModel):
    email: str


class UpdatePassword(BaseModel):
    token: str
    password: str
    password2: str

async def get_form_data(request: Request) -> dict:
    form_data = await request.form()
    return dict(form_data)

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

@router.post("/token")
async def login_for_access_token(response: Response, form_data: dict = Depends(get_form_data), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.get("username"), form_data.get("password"), db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect")
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@router.get("/logout1")
async def logout(request: Request):
    msg = "Logout Successfully"
    response = templates.TemplateResponse("login.html",{"request": request, "msg": msg})
    response.delete_cookie("access_token")
    return response

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...), firstname: str = Form(...), lastname: str = Form(...), password: str= Form(...), password2: str = Form(...), db: Session = Depends(get_db)):
    validation1 = db.query(models.USERS).filter(models.USERS.username == username).first()

    validation2 = db.query(models.USERS).filter(models.USERS.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = models.USERS()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@router.post("/forgot_password", response_class=HTMLResponse)
async def forgot_password(response: Response, form_data: ForgotPassword = Depends()):
    user = db.query(models.USERS).filter(models.USERS.email == form_data.email).first()

    if not user:
        msg = "User not found with this email"
    else:
        # Here you should send an email to the user with a password reset link
        # The password reset link should contain a unique token that identifies the user
        msg = "A password reset link has been sent to your email."

    return templates.TemplateResponse("forgot_password.html",{"request": request, "msg": msg})

@router.post("/update_password", response_class=HTMLResponse)
async def update_password(response: Response, form_data: UpdatePassword):
    if password == password2:
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

    return templates.TemplateResponse("update_password.html", {"request": request, "msg": msg})
