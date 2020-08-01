import ast
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import *
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return "Main Page"


@app.get("/image")
def image():
    return "Main Image Loadout"

# TODO: Validate things
@app.post("/grid")
def grid(points):
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
    centers = ast.literal_eval(points)

    points = []
    for center in centers:
        x, y= center["center"]
        points.extend(PointsInCircum(x, y, 1.5, n = 20) )

    xx, yy = zip(*points)
    min_x = min(xx); min_y = min(yy); max_x = max(xx); max_y = max(yy)
    bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]    
    bbox += [bbox[0]]

    lower_left = bbox[0]
    upper_right = bbox[2]
    grid = get_geojson_grid(upper_right, lower_left , n=10)
    grid = all_grid(grid, centers)
    sem = 100

    for geo_json in grid:
        geo_json["prob_dist"] = geo_json["prob_dist"]/sem
        color = plt.cm.Greens(geo_json["prob_dist"])
        color = mpl.colors.to_hex(color)
        geo_json["color"] = color

    return "sex", grid