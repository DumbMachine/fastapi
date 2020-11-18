from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel

from config import Config


def create_app():
    app = FastAPI()

    origins = ["http://localhost", "http://localhost:8080"]

    app.add_middleware(
        DBSessionMiddleware,
        db_url=Config.SQLALCHEMY_DATABASE_URI,
        # CORSMiddleware,
        # allow_origins=["*"],
        # allow_credentials=True,
        # allow_methods=["*"],
        # allow_headers=["*"],
    )
    app.mount("/images", StaticFiles(directory="images"), name="images")
    Path(Config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    return app


app = create_app()
