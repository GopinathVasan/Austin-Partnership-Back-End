import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends,APIRouter,Request,Form
import models
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import SessionLocal, engine
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404:{"description":"Not Found"}}
)

models.Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db:SessionLocal()
        yield db
    finally:
        db.close()
class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str
    confirm_password: str

@router.get("/edit-password", response_class = HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit-password.html", {"request": request, "user": user})
