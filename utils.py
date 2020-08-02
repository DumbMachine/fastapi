import math
import random
import numpy as np

pi = math.pi
MOD = 0.0015

def get_geojson_grid(upper_right, lower_left, n=6):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids"s.

    lower_left: array_like
        The lower left hand corner of "grid of grids" s.

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """

    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties": {
                            "lower_left": lower_left[::-1],
                            "upper_right": upper_right[::-1]
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

            all_boxes.append(geo_json)

    return all_boxes


def PointsInCircum(_x, y, r, n=100):
    ret = []
    for x in range(0, n+1):
        ret.append((
                _x+float(math.cos(2*pi/n*x)*r),
                y+float(math.sin(2*pi/n*x)*r)
            ))
    return ret


# def all_grid(grids, centers, rec):
#     """
#     Assign prob to all the grids
#     """
#     xx, yy = zip(*rec)
#     min_x = min(xx)
#     min_y = min(yy)
#     max_x = max(xx)
#     max_y = max(yy)

#     lat_steps = np.linspace(min_x, max_x, 3)

#     for grid in grids:
#         _points = grid["features"][0]["geometry"]["coordinates"][0][:-1]
#         xx, yy = zip(*_points)
#         centroid = (sum(xx) / len(_points), sum(yy) / len(_points))
#         temp = assign_prob(centroid, centers)
#         grid["prob_dist"] = sum(temp)
#     return grids

def all_grid(grid, centers):
    """
    Assign prob to all the grid
    """
    for _grid in grid:
        # _points = _grid["features"][0]["geometry"]["coordinates"][0][:-1]
        # # xx, yy = zip(*_points)
        # # centroid = (sum(xx) / len(_points), sum(yy) / len(_points))[::-1]
        # # temp =  assign_prob(centroid, centers)
        # _grid["prob_dist"] = sum(temp)
        _grid["prob_dist"] = random.random()
    return grid

def assign_prob(centroid, centers):
    """
    Assign probability of the `point` by comparing the distance with the centers
    """
    strip = [0.5, 0.17, 0.06, 0]
    prob = []
    for center in centers:
        distance = cal_dist(*centroid, *center["center"])
        strip_no = check_range_circle(distance, center["radius"]*MOD)
        if strip_no is not None:
            prob.append(center["trust"] * strip[strip_no])
    return prob


def check_range_circle(distance, radius):
    """
    Check in which range of the radius does the distance lie in
    """
    if distance < radius:
        prob = 0
    elif distance > radius and distance < 2*radius:
        prob = 1
    elif distance > 2 * radius and distance < 3*radius:
        prob = 2
    else:
        prob = -1
    return prob

def plot_circles(circle, all_three=False):
    """
    Plotting all the three circles
    ---------------------------------
    Example: 
        {
                "center": [29.961542, 76.823127],
                "radius": 120,
                "strip": [0.5, 0.17, 0.06],
                "color": 'crimson',
                "trust": 69
        }
    """
    import folium

    points, points1, points2 = [], [] ,[]

    x, y = circle["center"]
    points.extend(PointsInCircum(x, y, circle['radius']*0.0015, n=100))
    points1.extend(PointsInCircum(x, y, circle['radius']*2*0.0015, n=100))
    points2.extend(PointsInCircum(x, y, circle['radius']*3*0.0015, n=100))

    folium.PolyLine(points).add_to(m)
    folium.PolyLine(points1).add_to(m)
    folium.PolyLine(points2).add_to(m)


def check_range_rectangle(lat, lat_steps):
    """
    Check in which range of the radius does the distance lie in
    """
    for i in range(len(lat_steps)-1):
        renge = (lat_steps[i], lat_steps[i+1])
        if renge[0] < lat and lat > renge[1]:
            return i
    return None

def cal_dist(x1, y1, x2, y2):
    """
    Calculate the distance between the two points
    """
    return math.hypot(x2-x1, y2-y1)
