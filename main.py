from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080"]

import numpy as np
import pandas as pd

df = pd.read_csv("/home/dumbmachine/work/experiment/dietcare-frontend/fastapi/RAW_recipes.csv")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Main Page"

@app.post("/recipe")
def recipe(index: int):
    print(index)
    temp = df.loc[index].to_dict()
    for key, item in temp.items():
        if "numpy" in str(type(item)):
            temp[key] = item.tolist()
    return temp

