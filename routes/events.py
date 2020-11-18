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


@router.get("/create_event", response_class=HTMLResponse)
def create_event(request: Request):
    """Create an Event using Form"""
    return templates.TemplateResponse("eventForm.html", {"request": request})


@router.get("/delete_event", response_class=HTMLResponse)
def delete_event(request: Request):
    """delete an Event using Form"""
    return templates.TemplateResponse("deleteEventForm.html", {"request": request})


@router.post("/event")
def create_event_api(
    request: Request,
    id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    eventDate: str = Form(...),
    location: str = Form(...),
    allowedAttendees: str = Form(...),
    waitlist: str = Form(...),
    startTime: str = Form(...),
    endTime: str = Form(...),
):

    form = locals()
    _ = form.pop("request")
    image = form.pop("image")
    print(form)

    if image.filename:
        path = Config.IMAGES_FOLDER + "/" +image.filename
        # path = os.path.join(Config.IMAGES_FOLDER, image.filename)

        with open(path, "wb") as f:
            f.write(image.file.read())

        form["image"] = path

        try:
            database.insert_event(data=form)
            return "200", "Event Registry Made"
        except Exception as e:
            return {"status": "400", "Error" :f"{str(e)}"}
            # add code to remove the uploaded file
            # if the insert to database fails

    return "400", f"Error as image was not uploaded"


@router.get("/event/{eid}")
def show_event_api(eid: int):
    """Return a table showing the details from this event"""
    event = database.get_event(eid)
    return event


@router.post("/event/delete")
def delete_event_api(id: str = Form(...)):
    """Return a table showing the details from this event"""
    print(id)
    event = database.remove_event(id)
    if event == "Event Not Found":
        return event
    return event, "Deletion Successful"


@router.get("/list_event_upcoming", response_class=HTMLResponse)
def list_event_upcoming(request: Request):
    """Create an user using Form"""
    events = database.get_event_all()
    events = sorted(
        events, key=lambda event: datetime.strptime(event.eventDate, "%Y-%m-%d")
    )

    events = [
        event
        for event in events
        if datetime.strptime(event.eventDate, "%Y-%m-%d") > datetime.now()
    ]
    if len(events):
        return templates.TemplateResponse(
            "eventsListing.html",
            {"request": request, "eventsType": "upcoming", "events": events},
        )
    return "Event Not Found"


@router.get("/list_event_all", response_class=HTMLResponse)
def list_event_all(request: Request):
    """Create an user using Form"""
    events = database.get_event_all()
    from datetime import datetime

    events = sorted(
        events, key=lambda event: datetime.strptime(event.eventDate, "%Y-%m-%d")
    )

    if len(events):
        return templates.TemplateResponse(
            "eventsListing.html",
            {"request": request, "eventsType": "all", "events": events},
        )
    return "Event Not Found"
