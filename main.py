import folium
import random
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from temp import *
from utils import *
from glob import glob
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

N = 10
SATELITE = glob("satelite/*")
DEGREE = 90
TILE = 'Stamen Terrain'
FILENAME = "html/file.html"
origins = ["http://localhost", "http://localhost:8080"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/satelite", StaticFiles(directory="satelite"), name="satelite")


@app.get("/")
def home():
    return "Main Page"


@app.post("/model")
def model(item: dict):
    """
    Retrive information from the image processing api

    Schema for dict: 

        {
            "point" : [
                [10.171054833, 75.870382],
                [12.171054833, 75.970382]
            ]
        }

    """
    filename = random.choice(SATELITE)
    prob = 0
    if "HIGH" in filename:
        prob = 1
    response = {
        "query": item,
        "response": {
            "prob": prob,
            "image": FileResponse(filename, media_type='application/octet-stream', filename=filename)

        }
    }
    return response


@app.post("/models")
def models(item: dict):
    """
    Retrive information from the image processing api

    Schema for dict: 

        {
            "point" : [
                [10.171054833, 75.870382],
                [12.171054833, 75.970382]
            ]
        }

    """
    response = {"query": item, "response": []}
    for filename in SATELITE:
        prob = 0
        if "HIGH" in filename:
            prob = 1
        response["response"].append({
            "prob": prob,
            "image": FileResponse(filename, media_type='application/octet-stream', filename=filename)})
    return response


@app.post("/rect")
def rect(item: dict):
    """
    If there is no `Line` send "line": []

    If there is no `circles` send "circles": []

        example = {
            "line": [
                [
                    10.171054833,
                    75.870382
                ],
                [
                    12.171054833,
                    75.970382
                ],
                10
            ],
            "circles": [
                {
                    "center": [
                        10.171054833622044,
                        75.87038261100483
                    ],
                    "radius": 5.251052195950642
                },
                {
                    "center": [
                        10.337583,
                        75.420917
                    ],
                    "radius": 10.530432089900206
                },
                {
                    "center": [
                        10.420933,
                        75.872667
                    ],
                    "radius": 4.686149805543993
                }
            ]
        }
    """
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(
            zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(
                x, y, circle['radius']*1*0.02, n=100))  # 6,092 km
            points1.extend(PointsInCircum(
                x, y, circle['radius']*2*0.02, n=100))
            points2.extend(PointsInCircum(
                x, y, circle['radius']*3*0.02, n=100))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

    if line:
        line_grid = []
        (lat1, lon1), (lat2, lon2), width = line
        m = folium.Map(zoom_start=5, location=line[0],  tiles=TILE)
        for i in range(1, 4)[::-1]:
            DEGREE = 90
            rectangle = [
                displace(lat1, lon1, DEGREE, width*i)[::-1],
                displace(lat1, lon1, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, DEGREE, width*i)[::-1]
            ]
            rectangle += [rectangle[0]]
            all_points.extend([rec[::-1] for rec in rectangle])

    if all_points:
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        # bbox += [bbox[0]]
        return bbox

    return "None", "There was problem with your data"


@app.post("/rect/plot")
def rect_plot(item: dict):
    """
    If there is no `Line` send "line": []

    If there is no `circles` send "circles": []

        example = {
            "line": [
                [
                    10.171054833,
                    75.870382
                ],
                [
                    12.171054833,
                    75.970382
                ],
                10
            ],
            "circles": [
                {
                    "center": [
                        10.171054833622044,
                        75.87038261100483
                    ],
                    "radius": 5.251052195950642
                },
                {
                    "center": [
                        10.337583,
                        75.420917
                    ],
                    "radius": 10.530432089900206
                },
                {
                    "center": [
                        10.420933,
                        75.872667
                    ],
                    "radius": 4.686149805543993
                }
            ]
        }
    """
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(
            zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100))
            points1.extend(PointsInCircum(
                x, y, circle['radius']*2*0.02, n=100))
            points2.extend(PointsInCircum(
                x, y, circle['radius']*3*0.02, n=100))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

    if line:
        line_grid = []
        (lat1, lon1), (lat2, lon2), width = line
        m = folium.Map(zoom_start=5, location=line[0],  tiles=TILE)
        for i in range(1, 4)[::-1]:
            DEGREE = 90
            rectangle = [
                displace(lat1, lon1, DEGREE, width*i)[::-1],
                displace(lat1, lon1, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, DEGREE, width*i)[::-1]
            ]
            rectangle += [rectangle[0]]
            all_points.extend([rec[::-1] for rec in rectangle])

    if all_points:
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        bbox += [bbox[0]]

        folium.PolyLine(bbox).add_to(m)
        m.save(FILENAME)
        return FileResponse(FILENAME, media_type='application/octet-stream', filename=FILENAME)

    return "None", "There was problem with your data"


@app.post("/grid")
def grid(item: dict):
    """
    If there is no `Line` send "line": []

    If there is no `circles` send "circles": []

            {
                "line": [
                    [
                        10.171054833,
                        75.870382
                    ],
                    [
                        12.171054833,
                        75.970382
                    ],
                    10
                ],
                "circles": [
                    {
                        "center": [
                            10.171054833622044,
                            75.87038261100483
                        ],
                        "radius": 5.251052195950642,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 75
                    },
                    {
                        "center": [
                            10.337583,
                            75.420917
                        ],
                        "radius": 10.530432089900206,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 57
                    },
                    {
                        "center": [
                            10.420933,
                            75.872667
                        ],
                        "radius": 4.686149805543993,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 25
                    }
                ]
            }
    """
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(
            zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(
                x, y, circle['radius']*1*0.02, n=100))  # 6,092 km
            circle["rad_strips"].append(distance_(points[0], circle["center"]))
            points1.extend(PointsInCircum(
                x, y, circle['radius']*2*0.02, n=100))
            circle["rad_strips"].append(
                distance_(points1[0], circle["center"]))
            points2.extend(PointsInCircum(
                x, y, circle['radius']*3*0.02, n=100))
            circle["rad_strips"].append(
                distance_(points2[0], circle["center"]))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

    if line:
        line_grid = []
        (lat1, lon1), (lat2, lon2), width = line
        m = folium.Map(zoom_start=5, location=line[0],  tiles=TILE)
        strip = [0.52, 0.223, 0.017][::-1]
        for i in range(1, 4)[::-1]:
            DEGREE = 90
            rectangle = [
                displace(lat1, lon1, DEGREE, width*i)[::-1],
                displace(lat1, lon1, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, DEGREE, width*i)[::-1]
            ]
            rectangle += [rectangle[0]]
            coordinates = rectangle
            geo_json = {"type": "FeatureCollection",
                        "properties": {
                            "lower_left": rectangle[0],
                            "upper_right": rectangle[2]
                        },
                        "features": []}

            grid_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                }
            }
            geo_json["features"].append(grid_feature)
            geo_json["prob"] = strip[3-i]
            color = plt.cm.Greens(geo_json["prob"])
            color = mpl.colors.to_hex(color)
            geo_json["color"] = color
            line_grid.append(geo_json)
            all_points.extend([rec[::-1] for rec in rectangle])
        #     folium.PolyLine([rec[::-1] for rec in rectangle]).add_to(m)

        DEGREE = 90
        rectangle = [
            displace(lat1, lon1, DEGREE, width),
            displace(lat1, lon1, -DEGREE, width),
            displace(lat2, lon2, -DEGREE, width),
            displace(lat2, lon2, DEGREE, width)
        ]
        rectangle += [rectangle[0]]
        all_points.extend(rectangle)

    if all_points:
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        bbox += [bbox[0]]

        lower_left, upper_right = bbox[0], bbox[2]
        grid = get_geojson_grid(upper_right, lower_left, n=N)
        new_grid = all_grid(grid, circles)

        new_grid += line_grid
        return new_grid
    else:
        return "What THe Fuck are You Doing"


@app.post("/grid/plot")
def grid_plot(item: dict):
    """
    If there is no `Line` send "line": []

    If there is no `circles` send "circles": []

            {
                "line": [
                    [
                        10.171054833,
                        75.870382
                    ],
                    [
                        12.171054833,
                        75.970382
                    ],
                    10
                ],
                "circles": [
                    {
                        "center": [
                            10.171054833622044,
                            75.87038261100483
                        ],
                        "radius": 5.251052195950642,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 75
                    },
                    {
                        "center": [
                            10.337583,
                            75.420917
                        ],
                        "radius": 10.530432089900206,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 57
                    },
                    {
                        "center": [
                            10.420933,
                            75.872667
                        ],
                        "radius": 4.686149805543993,
                        "strip": [
                            0.5,
                            0.2,
                            0.1
                        ],
                        "trust": 25
                    }
                ]
            }
    """
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(
            zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(
                x, y, circle['radius']*1*0.02, n=100))  # 6,092 km
            circle["rad_strips"].append(distance_(points[0], circle["center"]))
            points1.extend(PointsInCircum(
                x, y, circle['radius']*2*0.02, n=100))
            circle["rad_strips"].append(
                distance_(points1[0], circle["center"]))
            points2.extend(PointsInCircum(
                x, y, circle['radius']*3*0.02, n=100))
            circle["rad_strips"].append(
                distance_(points2[0], circle["center"]))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

    if line:
        line_grid = []
        (lat1, lon1), (lat2, lon2), width = line
        m = folium.Map(zoom_start=5, location=line[0],  tiles=TILE)
        strip = [0.52, 0.223, 0.017][::-1]
        for i in range(1, 4)[::-1]:
            DEGREE = 90
            rectangle = [
                displace(lat1, lon1, DEGREE, width*i)[::-1],
                displace(lat1, lon1, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, -DEGREE, width*i)[::-1],
                displace(lat2, lon2, DEGREE, width*i)[::-1]
            ]
            rectangle += [rectangle[0]]
            coordinates = rectangle
            geo_json = {"type": "FeatureCollection",
                        "properties": {
                            "lower_left": rectangle[0],
                            "upper_right": rectangle[2]
                        },
                        "features": []}

            grid_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                }
            }
            geo_json["features"].append(grid_feature)
            geo_json["prob"] = strip[3-i]
            color = plt.cm.Greens(geo_json["prob"])
            color = mpl.colors.to_hex(color)
            geo_json["color"] = color
            line_grid.append(geo_json)
            all_points.extend([rec[::-1] for rec in rectangle])
        #     folium.PolyLine([rec[::-1] for rec in rectangle]).add_to(m)

        DEGREE = 90
        rectangle = [
            displace(lat1, lon1, DEGREE, width),
            displace(lat1, lon1, -DEGREE, width),
            displace(lat2, lon2, -DEGREE, width),
            displace(lat2, lon2, DEGREE, width)
        ]
        rectangle += [rectangle[0]]
        all_points.extend(rectangle)

    if all_points:
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        bbox += [bbox[0]]

        lower_left, upper_right = bbox[0], bbox[2]
        grid = get_geojson_grid(upper_right, lower_left, n=N)
        new_grid = all_grid(grid, circles)
        new_grid += line_grid
        folium.PolyLine(bbox).add_to(m)

        for i, geo_json in enumerate(new_grid):
            color = geo_json["color"]
            gj = folium.GeoJson(geo_json,
                                style_function=lambda feature: {
                                    'color': color,
                                    'fillColor': color,
                                    #                             'fillOpacity':0.3,
                                })
            popup = folium.Tooltip(f"{geo_json['prob']}")
            gj.add_child(popup)
            m.add_child(gj)

        m.save(FILENAME)
        return FileResponse(FILENAME, media_type='application/octet-stream', filename=FILENAME)

    return None
