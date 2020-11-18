from sqlalchemy import exc
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Form, Request, UploadFile, File, APIRouter
from pydantic import BaseModel
import os
from .model import get_db

from config import Config

database = get_db()


router = APIRouter()

templates = Jinja2Templates(directory="html")


@router.get("/create_user", response_class=HTMLResponse)
def create_user(request: Request):
    """Create an user using Form"""
    return templates.TemplateResponse("userForm.html", {"request": request})


@router.post("/user")
def create_user_api(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
):
    """
    Add user information to the database
    """

    form = locals()
    _ = form.pop("request")
    print(form)

    try:
        database.insert_user(data=form)
    except Exception as e:
        print(e)


@router.get("/user/{eid}")
def show_user_api(eid: int):
    """Return a table showing the details from this user"""
    user = database.get_user(eid)
    return user


@router.put("/user/{eid}")
def update_user_api(eid: int):
    """Return a table showing the details from this user"""
    raise NotImplementedError


@router.post("/user/delete")
def delete_event_api(id: str = Form(...)):
    """Return a table showing the details from this user"""
    print(id)
    user = database.remove_event(id)
    if user == -1:
        return user
    return user, "Deletion Successful"
