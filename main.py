import os

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import exc

from routes import attend, events, users

# import model


app = FastAPI()

FILENAME = "html/file.html"
UPLOAD_FOLDER = "images"
origins = ["http://localhost", "http://localhost:8080"]

# database = model.get_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="html")


"""
TODO:
1. Update Api
"""

app.include_router(users.router)
app.include_router(attend.router)
app.include_router(events.router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    supported_actions = [
        # Event Related Api
        ["create_event", "Create Event"],
        ["delete_event", "Delete Event"],
        ["list_event_upcoming", "List Upcoming Events"],
        ["list_event_all", "List All Events"],
        # User Related Api
        ["create_user", "Create User"],
        ["delete_user", "Delete User"],
        # Attendence Api
        ["attend", "Attend Event(for a logged user)"],
        # ["attendance", "Get Attendees of an event"],
    ]
    return templates.TemplateResponse(
        "main.html", {"request": request, "actions": supported_actions}
    )
