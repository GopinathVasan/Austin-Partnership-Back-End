from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,Path
from starlette import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import USERS
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta,datetime

router = APIRouter(
    prefix='/auth',
    tags= ['auth'])


SECRET_KEY = '02fedfbe585ad82f54aa63f1f6c933312063de2e46ab482af8a0ab0fb6b80913'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes =['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
 
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
 
db_dependency = Annotated[Session, Depends(get_db)]   

def authenticate_user(username: str, password: str, db):
    user = db.query(USERS).filter(USERS.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user

   

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
   
   encode = {'sub': username, 'id':user_id}
   expires = datetime.utcnow() + expires_delta
   encode.update({'exp': expires})
   return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
   

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       username: str = payload.get('sub')
       user_id: int = payload.get('id')
       if username is None or user_id is None:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              details='Could not validate user.')
       return {'username': username, 'id':user_id}    
    except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              details='Could not validate user.')




@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
   create_user_request:CreateUserRequest):
    create_user_model = USERS(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
   USERS = authenticate_user(form_data.username, form_data.password,db)
   if not USERS:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              details='Could not validate user.') 
   token = create_access_token(USERS.username, USERS.id, timedelta(minutes=20))
   return {'access_token': token, 'token_type': 'bearer'}
   