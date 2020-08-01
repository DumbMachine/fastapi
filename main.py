from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return "Main Page"


@app.get("/image")
def image():
    return "Main Image Loadout"

@app.post("/grid")
def grid(points):

    return points

