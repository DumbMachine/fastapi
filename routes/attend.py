from datetime import datetime
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


@router.get("/attend", response_class=HTMLResponse)
def attend_form(request: Request):
    """Create an user using Form"""
    return templates.TemplateResponse("attendUserForm.html", {"request": request})


@router.post("/attend")
def create_attend_api(request: Request, id: str = Form(...), eventid: str = Form(...)):

    try:
        # check if the user exists
        user = database.get_user(uid=id)
        if user == "User Not Found":
            return "404", "Attendance not possible as the User does not exist"

        # check if the event exists
        event = database.get_event(eid=eventid)
        if event == "Event Not Found":
            return "404", "Attendance not possible as the Event does not exist"

        # if the user has an upcoming booking, don't allow for anymore bookings
        if (
            user.eid != None
            and datetime.strptime(event.eventDate, "%Y-%m-%d") > datetime.now()
        ):
            return "400", "This User Already has a pending Event"

        database.attend_event(userid=id, eventid=eventid)
        database.commit()
        return "300", "Even Listing was inserted"

    except exc.IntegrityError as e:
        database.rollback()
        return "400", f"{e}"
        # add code to remove the uploaded file
        # if the insert to database fails


@router.get("/attendance/{eventid}", response_class=HTMLResponse)
def attendance_listing(request: Request, eventid: str):
    """Create an user using Form"""
    users = database.get_user_all()
    users = [user.name for user in users if user.eid == eventid]
    return templates.TemplateResponse("eventAttendance.html", {"request": request, "eventid": eventid, "data": [len(users), users]})

