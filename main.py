import model

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

FILENAME = "html/file.html"
origins = ["http://localhost", "http://localhost:8080"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/data", StaticFiles(directory="data"), name="data")

templates = Jinja2Templates(directory="html")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    supported_actions = [
        ["create_event", "Create Event"],
        ["delete_event", "Delete Event"],
        ["list_event_upcoming", "List Upcoming Events"],
        ["list_event_all", "List All Events"],
        ["create_user", "Create User"],
        ["delete_user", "Delete User"],
        ["attend_ ","Attend Event(for a logged user)"],
        ["get_users", "Get Attendees of an event"]
    ]
    return templates.TemplateResponse(
        "main.html", {
            "request": request,
            "actions": supported_actions
        })


@app.get("/create_event", response_class=HTMLResponse)
def home(request: Request):
    """Create an Event using Form
    """
    return templates.TemplateResponse(
        "eventForm.html", {
            "request": request
        })
