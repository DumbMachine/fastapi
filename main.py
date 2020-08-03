import folium
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from temp import *
from utils import *
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/rect")
def rect(item: dict):
    """
    POST REQUEST:
    =============
    class Center:
        radius: int
        center: tuple
        trust: int
    """
    circles = item["circle"]
    bbox = None
    m = folium.Map(zoom_start=5, location=circles[0]["center"],  tiles="CartoDB dark_matter")
    if circles is not None: # draw the circles
        all_points = []
        for circle in circles:
            points, points1, points2 = [], [], []

            x, y = circle["center"]

        #     points2.extend(PointsInCircum(x, y, circle['radius']*3*0.0015, n=100))
            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100)) #6,092 km
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
        #     points.extend(getCoordinates(x, y, circle['radius']*1, n=100)) #6,092 km
        #     points1.extend(getCoordinates(x, y, circle['radius']*2, n=100))
        #     points2.extend(getCoordinates(x, y, circle['radius']*3, n=100))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

            folium.PolyLine(points, color="green", popup=points[0]).add_to(m)
            folium.PolyLine(points1, color="red", popup=points1[0]).add_to(m)
            folium.PolyLine(points2, color="blue", popup=points2[0]).add_to(m)

        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        return bbox

@app.post("/grid")
def grid(item: dict):
    """
    TEST Query/n: 
        {
            "line": [
                [10.171054833, 75.870382],
                [12.171054833, 75.970382], 10
            ],
        "circles": [{"center": [10.171054833622044, 75.87038261100483],
        "radius": 5.251052195950642,
        "strip": [0.5,0.2,0.1],
        "trust": 75},
        {"center": [10.337583, 75.420917],
        "radius":  10.530432089900206,
        "strip": [0.5,0.2,0.1],
        "trust": 57},
            {"center": [10.420933, 75.872667],
        "radius":   4.686149805543993,
        "strip": [0.5,0.2,0.1],
        "trust": 25}]
            }
    """
    N = 30
    TILE = 'Stamen Terrain'
    DEGREE = 90
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100)) #6,092 km
            circle["rad_strips"].append(distance_(points[0], circle["center"]))
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            circle["rad_strips"].append(distance_(points1[0], circle["center"]))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
            circle["rad_strips"].append(distance_(points2[0], circle["center"]))

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
            rectangle+= [rectangle[0]]
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
        rectangle+= [rectangle[0]]
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
        {
            "line": [
                [10.171054833, 75.870382],
                [12.171054833, 75.970382], 10
            ],
        "circles": [{"center": [10.171054833622044, 75.87038261100483],
        "radius": 5.251052195950642,
        "strip": [0.5,0.2,0.1],
        "trust": 75},
        {"center": [10.337583, 75.420917],
        "radius":  10.530432089900206,
        "strip": [0.5,0.2,0.1],
        "trust": 57},
            {"center": [10.420933, 75.872667],
        "radius":   4.686149805543993,
        "strip": [0.5,0.2,0.1],
        "trust": 25}]
            }
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    options.binary_location = "/app/.apt/usr/bin/google-chrome-stable"
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)
    driver.quit()
    print("DRIVER WAS OPENEND")
        
    """
    N = 30
    TILE = 'Stamen Terrain'
    DEGREE = 90
    line_grid = []
    all_points = []
    line = item["line"]
    circles = item["circles"]
    all_points = []
    if circles:
        m = folium.Map(zoom_start=5, location=circles[0]["center"],  tiles=TILE)
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100)) #6,092 km
            circle["rad_strips"].append(distance_(points[0], circle["center"]))
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            circle["rad_strips"].append(distance_(points1[0], circle["center"]))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
            circle["rad_strips"].append(distance_(points2[0], circle["center"]))

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
            rectangle+= [rectangle[0]]
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
        rectangle+= [rectangle[0]]
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

        m.save("test.html")
        return FileResponse("test.html", media_type='application/octet-stream', filename="test.html")

    return None

@app.post("/line/")
def rect_from_line(item: dict):
    """
    {
        "data": [
            [29.961542, 76.823127],
            [32.961542, 76.823127],
            100
        ],
        "circle": [{
            "center": [29.961542, 76.823127],
            "radius": 100,
            "trust": 69
        },
        {
            "center": [31.961542, 86.823127],
            "radius": 220,
            "trust": 69
        }]
    }
    """
    data = item.pop("data", None)
    circles = item.pop("circle", None)
    rectangle = []
    if data is not None:
        (lat1, lon1), (lat2, lon2), width = data

        width *= 5
        DEGREE = 90
        rectangle = [
                displace(lat1, lon1, DEGREE, width),
                displace(lat1, lon1, -DEGREE, width),
                displace(lat2, lon2, -DEGREE, width),
                displace(lat2, lon2, DEGREE, width)
        ]
    if circles is not None: # draw the circles
        all_points = []
        for circle in circles:
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100)) #6,092 km
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
            
            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

        rectangle += [rectangle[0]]
        all_points.extend(rectangle)
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        # bbox += [bbox[0]]

        return bbox


    return rectangle


@app.post("/line/plot")
def rect_from_line_plot(item: dict):
    """
    [
            [29.961542, 76.823127],
            [32.961542, 76.823127],
            100
    ]
        (OR)
    {
        "data": [
            [29.961542, 76.823127],
            [32.961542, 76.823127],
            100
        ],
        "circles": [{
            "center": [29.961542, 76.823127],
            "radius": 100,
            "trust": 69
        },
        {
            "center": [31.961542, 86.823127],
            "radius": 220,
            "trust": 69
        }]
    }
    
    """
    data = item.pop("data", None)
    circles = item.pop("circle", None)
    rectangle = []
    (lat1, lon1), (lat2, lon2), width = (0, 0), (0, 0), 0

    if data is not None:
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
    if circles is not None: # draw the circles
        all_points = []
        for circle in circles:
            points, points1, points2 = [], [], []

            x, y = circle["center"]
    
            points.extend(PointsInCircum(x, y, circle['radius']*0.05, n=100)) #6,092 km
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.05, n=100))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.05, n=100))
            
            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

        if rectangle:
            rectangle += [rectangle[0]]
        all_points.extend(rectangle)
        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        bbox += [bbox[0]]
        rectangle = bbox

    m = folium.Map(zoom_start=5, location=[lat1, lon1],  tiles="CartoDB dark_matter")
    folium.PolyLine(bbox).add_to(m)
    # folium.PolyLine(all_points).add_to(m)
    m.save("test.html")

    return FileResponse("test.html", media_type='application/octet-stream', filename="test.html")

@app.post("/circle/")
def rect_from_circle(item: dict):
    """
    {
        "data": [
            [29.961542, 76.823127],
            [32.961542, 76.823127],
            100
        ],
        "circle": [{
            "center": [29.961542, 76.823127],
            "radius": 100,
            "trust": 69
        },
        {
            "center": [31.961542, 86.823127],
            "radius": 220,
            "trust": 69
        }]
    }
    """
    circles = item["circle"]
    bbox = None
    m = folium.Map(zoom_start=5, location=circles[0]["center"],  tiles="CartoDB dark_matter")
    if circles is not None: # draw the circles
        all_points = []
        for circle in circles:
            points, points1, points2 = [], [], []

            x, y = circle["center"]

        #     points2.extend(PointsInCircum(x, y, circle['radius']*3*0.0015, n=100))
            points.extend(PointsInCircum(x, y, circle['radius']*1*0.0111112, n=100)) #6,092 km
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
        #     points.extend(getCoordinates(x, y, circle['radius']*1, n=100)) #6,092 km
        #     points1.extend(getCoordinates(x, y, circle['radius']*2, n=100))
        #     points2.extend(getCoordinates(x, y, circle['radius']*3, n=100))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

            folium.PolyLine(points, color="green", popup=points[0]).add_to(m)
            folium.PolyLine(points1, color="red", popup=points1[0]).add_to(m)
            folium.PolyLine(points2, color="blue", popup=points2[0]).add_to(m)

        xx, yy = zip(*all_points)
        min_x = min(xx)
        min_y = min(yy)
        max_x = max(xx)
        max_y = max(yy)
        bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        bbox += [bbox[0]]

        lower_left, upper_right = bbox[0], bbox[2]
        grid = get_geojson_grid(upper_right, lower_left, n=10)
        for _grid in grid:
            _grid["prob"] = random.random()
            color = plt.cm.Greens(_grid["prob"])
            color = mpl.colors.to_hex(color)
            _grid["color"] = color

    return grid
    


@app.post("/circle/plot")
def rect_from_circle_plot(item: dict):
    """
    {
        "circle": [{
            "center": [29.961542, 76.823127],
            "radius": 10,
            "trust": 69
        },
        {
            "center": [31.961542, 86.823127],
            "radius": 20,
            "trust": 69
        }]
    }
    """
    N = 30
    circles = item["circle"]
    m = folium.Map(zoom_start=5, location=circles[0]["center"],  tiles="CartoDB dark_matter")
    if circles is not None: # draw the circles
        all_points = []
        for circle in circles:
            circle["rad_strips"] = []
            points, points1, points2 = [], [], []

            x, y = circle["center"]

            points.extend(PointsInCircum(x, y, circle['radius']*1*0.02, n=100)) #6,092 km
            circle["rad_strips"].append(distance_(points[0], circle["center"]))
            points1.extend(PointsInCircum(x, y, circle['radius']*2*0.02, n=100))
            circle["rad_strips"].append(distance_(points1[0], circle["center"]))
            points2.extend(PointsInCircum(x, y, circle['radius']*3*0.02, n=100))
            circle["rad_strips"].append(distance_(points2[0], circle["center"]))

            all_points.extend(points)
            all_points.extend(points1)
            all_points.extend(points2)

            folium.PolyLine(points, color="green", popup=points[0]).add_to(m)
            folium.PolyLine(points1, color="red", popup=points1[0]).add_to(m)
            folium.PolyLine(points2, color="blue", popup=points2[0]).add_to(m)

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

        for i, geo_json in enumerate(new_grid):
            color = geo_json["color"]

            gj = folium.GeoJson(geo_json,
                                style_function=lambda feature, color=color: {
                                    'fillColor': color,
                                    'color': "black",
                                    'weight': 2,
                                    'dashArray': '5, 5',
                                    'fillOpacity': 0.55,
                                })
            popup = folium.Tooltip(f"{geo_json['prob']}")
            gj.add_child(popup)
            m.add_child(gj)

        folium.PolyLine(bbox).add_to(m)
        m.save("test.html")

        return FileResponse("test.html", media_type='application/octet-stream', filename="test.html")


    return None
