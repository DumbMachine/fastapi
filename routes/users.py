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
        return "200", "User Registry Made"
    except Exception as e:
        return {"status": "400", "Error": f"{str(e)}"}


@router.get("/user/{eid}")
def show_user_api(eid: int):
    """Return a table showing the details from this user"""
    user = database.get_user(eid)
    return user


@router.put("/user/{eid}")
def update_user_api(eid: int):
    """Return a table showing the details from this user"""
    raise NotImplementedError


@router.get("/delete_user", response_class=HTMLResponse)
def dalete_user(request: Request):
    """Create an user using Form"""
    return templates.TemplateResponse("userDeleteForm.html", {"request": request})


@router.post("/user/delete")
def delete_event_api(id: str = Form(...)):
    """Return a table showing the details from this user"""
    user = database.remove_user(id)
    if user == "User Not Found":
        return user, "Deletion Unsuccessful"
    return user, "Deletion Successful"
