import os
import model

from pydantic import BaseModel
from fastapi import Form, FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import exc

app = FastAPI()

FILENAME = "html/file.html"
UPLOAD_FOLDER = "images"
origins = ["http://localhost", "http://localhost:8080"]

database = model.get_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="html")


'''
TODO:
1. Update Api
'''


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    supported_actions = [
        ["create_event", "Create Event"],
        ["delete_event", "Delete Event"],
        ["list_event_upcoming", "List Upcoming Events"],
        ["list_event_all", "List All Events"],
        ["create_user", "Create User"],
        ["delete_user", "Delete User"],
        ["attend_ ", "Attend Event(for a logged user)"],
        ["get_users", "Get Attendees of an event"]
    ]
    return templates.TemplateResponse(
        "main.html", {
            "request": request,
            "actions": supported_actions
        })


@app.get("/list_event_upcoming", response_class=HTMLResponse)
def list_event_upcoming(request: Request):
    """Create an user using Form
    """
    events = database.get_event_all()
    from datetime import datetime
    events = sorted(events, key=lambda event: datetime.strptime(
        event.eventDate, "%Y-%m-%d"))

    events = [event for event in events if datetime.strptime(
        event.eventDate, "%Y-%m-%d") > datetime.now()]

    return templates.TemplateResponse(
        "eventsListing.html", {
            "request": request,
            "eventsType": "upcoming",
            "events": events
        })


@app.get("/list_event_all", response_class=HTMLResponse)
def list_event_all(request: Request):
    """Create an user using Form
    """
    events = database.get_event_all()
    from datetime import datetime
    events = sorted(events, key=lambda event: datetime.strptime(
        event.eventDate, "%Y-%m-%d"))

    return templates.TemplateResponse(
        "eventsListing.html", {
            "request": request,
            "eventsType": "all",
            "events": events
        })


@app.get("/attend_", response_class=HTMLResponse)
def list_user_all(request: Request):
    """Create an user using Form
    """
    return templates.TemplateResponse(
        "attendUserForm.html", {
            "request": request
        })


@app.post("/attend")
def create_event_api(
    request: Request,
    id: str = Form(...),
    eventid: str = Form(...)

):

    form = locals()
    _ = form.pop("request")
    image = form.pop("image")
    print(form)

    path = os.path.join(UPLOAD_FOLDER, image.filename)

    with open(path, 'wb') as f:
        f.write(image.file.read())

    form["image"] = path

    try:
        database.insert_event(data=form)
        database.commit()
        return "300", "Even Listing was inserted"
    except exc.IntegrityError as e:
        database.rollback()
        return "400", f"{e}"
        # add code to remove the uploaded file
        # if the insert to database fails




@app.get("/create_event", response_class=HTMLResponse)
def create_event(request: Request):
    """Create an Event using Form
    """
    return templates.TemplateResponse(
        "eventForm.html", {
            "request": request
        })


@app.get("/delete_event", response_class=HTMLResponse)
def delete_event(request: Request):
    """delete an Event using Form
    """
    return templates.TemplateResponse(
        "deleteEventForm.html", {
            "request": request
        })


@app.post("/event")
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
    endTime: str = Form(...)

):

    form = locals()
    _ = form.pop("request")
    image = form.pop("image")
    print(form)

    path = os.path.join(UPLOAD_FOLDER, image.filename)

    with open(path, 'wb') as f:
        f.write(image.file.read())

    form["image"] = path

    try:
        database.insert_event(data=form)
    except Exception as e:
        print(e)
        # add code to remove the uploaded file
        # if the insert to database fails


@app.get("/event/{eid}")
def show_event_api(eid: int):
    """Return a table showing the details from this event
    """
    event = database.get_event(eid)
    return event

@app.post("/event/delete")
def delete_event_api(id: str = Form(...)):
    """Return a table showing the details from this event
    """
    print(id)
    event = database.remove_event(id)
    if event == -1:
        return event
    return event, "Deletion Successful"



@app.get("/create_user", response_class=HTMLResponse)
def create_user(request: Request):
    """Create an user using Form
    """
    return templates.TemplateResponse(
        "userForm.html", {
            "request": request
        })


@app.post("/user")
def create_user_api(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
):

    form = locals()
    _ = form.pop("request")
    print(form)

    try:
        database.insert_user(data=form)
    except Exception as e:
        print(e)


@app.get("/user/{eid}")
def show_user_api(eid: int):
    """Return a table showing the details from this user
    """
    user = database.get_user(eid)
    return user


@app.put("/user/{eid}")
def update_user_api(eid: int):
    """Return a table showing the details from this user
    """
    raise NotImplementedError


@app.post("/user/delete")
def delete_event_api(id: str = Form(...)):
    """Return a table showing the details from this user
    """
    print(id)
    user = database.remove_event(id)
    if user == -1:
        return user
    return user, "Deletion Successful"
