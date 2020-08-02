import ast
import folium
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import *
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# import io
# from PIL import Image
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

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


@app.post("/image")
def image():
    return "Main Image Loadout"

# TODO: Validate things


@app.post("/grid")
def grid(points: list):
    """
    POST REQUEST:
    =============
    class Center:
        radius: int
        center: tuple
        trust: int
        strip_trust: tuple
    """
    centers = points

    points = []
    for center in centers:
        x, y = center["center"]
        points.extend(PointsInCircum(x, y, 1.5, n=20))

    xx, yy = zip(*points)
    min_x = min(xx)
    min_y = min(yy)
    max_x = max(xx)
    max_y = max(yy)
    bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    bbox += [bbox[0]]

    lower_left = bbox[0]
    upper_right = bbox[2]
    grid = get_geojson_grid(upper_right, lower_left, n=10)
    grid = all_grid(grid, centers)
    sem = 100

    for geo_json in grid:
        geo_json["prob_dist"] = geo_json["prob_dist"]/sem
        color = plt.cm.Greens(geo_json["prob_dist"])
        color = mpl.colors.to_hex(color)
        geo_json["color"] = color

    return grid



@app.post("/line/")
def rect_from_line(data: list):
    (lat1, lon1), (lat2, lon2), width = data
    width *= 5
    DEGREE = 90
    rectangle = [
        (
            displace(lat1, lon1, DEGREE, width*1.25),
            displace(lat1, lon1, -DEGREE, width*1.25)
        ),
        (
            displace(lat2, lon2, DEGREE, width),
            displace(lat2, lon2, -DEGREE, width)
        )
    ]
    return rectangle

@app.post("/line/plot")
def rect_from_line_plot(data: list):
    """
    [
            [29.961542, 76.823127],
            [32.961542, 76.823127],
            100
    ]
    """
    (lat1, lon1), (lat2, lon2), width = data
    width *= 5
    DEGREE = 90
    rectangle = [
        (
            displace(lat1, lon1, DEGREE, width*1.25),
            displace(lat1, lon1, -DEGREE, width*1.25)
        ),
        (
            displace(lat2, lon2, DEGREE, width),
            displace(lat2, lon2, -DEGREE, width)
        )
    ]
    m = folium.Map(zoom_start=5, location=[lat1, lon1],  tiles="CartoDB dark_matter")
    rectangle += [rectangle[0]]
    folium.PolyLine(rectangle).add_to(m)

    m.save("test.html")
    return FileResponse("test.html", media_type='application/octet-stream', filename="test.html")


@app.post("/grid/plot")
def grid_plot(points: list):
    """
    POST REQUEST:
    =============
    class Center:
        radius: int
        center: tuple
        trust: int
        strip_trust: tuple
    """
    # parsing the list of dicts
    # centers = ast.literal_eval(points)
    centers = points
    points = []
    for center in centers:
        x, y = center["center"]
        points.extend(PointsInCircum(x, y, 1.5, n=20))

    xx, yy = zip(*points)
    min_x = min(xx)
    min_y = min(yy)
    max_x = max(xx)
    max_y = max(yy)
    bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    bbox += [bbox[0]]

    lower_left = bbox[0]
    upper_right = bbox[2]
    grid = get_geojson_grid(upper_right, lower_left, n=10)
    grid = all_grid(grid, centers)
    sem = 100
    m = folium.Map(zoom_start=5, location=[
                   55, 0],  tiles="CartoDB dark_matter")

    for i, geo_json in enumerate(grid):
        geo_json["prob_dist"] = geo_json["prob_dist"]/sem
        color = plt.cm.Greens(geo_json["prob_dist"])
        color = mpl.colors.to_hex(color)
        geo_json["color"] = color

        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature, color=color: {
                                'fillColor': color,
                                'color': "black",
                                'weight': 2,
                                'dashArray': '5, 5',
                                'fillOpacity': 0.55,
                            })
        popup = folium.Popup("example popup {}".format(abs(i-15)))
        gj.add_child(popup)
        m.add_child(gj)

    m.save("test.html")

    return FileResponse("test.html", media_type='application/octet-stream', filename="test.html")
