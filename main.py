import ast
import folium
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import *
from fastapi import FastAPI
from fastapi.responses import FileResponse
import io
from PIL import Image

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

    return grid

@app.post("/grid/plot")
def grid_plot(points):
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
    m = folium.Map(zoom_start = 5, location=[55, 0],  tiles="CartoDB dark_matter")

    for i, geo_json in enumerate(grid):
        geo_json["prob_dist"] = geo_json["prob_dist"]/sem
        color = plt.cm.Greens(geo_json["prob_dist"])
        color = mpl.colors.to_hex(color)
        geo_json["color"] = color

        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature, color=color: {
                                                                            'fillColor': color,
                                                                            'color':"black",
                                                                            'weight': 2,
                                                                            'dashArray': '5, 5',
                                                                            'fillOpacity': 0.55,
                                                                        })
        popup = folium.Popup("example popup {}".format(abs(i-15)))
        gj.add_child(popup)

        m.add_child(gj)
    
    m.save("test.html")

    return FileResponse('test.html')
"""

import ast
import requests

points = open("sarin.json", "r").read()
centers = ast.literal_eval(points)
requests.post("http://127.0.0.1:8000/(grid)", centers)

curl -X POST "http://127.0.0.1:8001/grid/plot?points=%5B%7B%27center%27%3A%20%2829.961264%2C%2076.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%2095%7D%2C%20%20%7B%27center%27%3A%20%2825.961264%2C%2076.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%2086%7D%2C%20%20%7B%27center%27%3A%20%2821.961264%2C%2072.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%203%7D%2C%20%20%7B%27center%27%3A%20%2839.961264%2C%2077.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%2013%7D%2C%20%20%7B%27center%27%3A%20%2832.961264%2C%2071.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%2041%7D%2C%20%20%7B%27center%27%3A%20%2829.961264%2C%2075.826217%29%2C%20%20%20%27radius%27%3A%2030%2C%20%20%20%27color%27%3A%20%27red%27%2C%20%20%20%27strip%27%3A%20%5B0.5%2C%200.3%2C%200.1%5D%2C%20%20%20%27trust%27%3A%2039%7D%5D" -H  "accept: application/json" -d ""

"""