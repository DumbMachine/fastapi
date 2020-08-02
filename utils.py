import math
import numpy as np

pi = math.pi

def get_geojson_grid(upper_right, lower_left, n=6):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids" (the default is the upper right hand [lat, lon] of the USA).

    lower_left: array_like
        The lower left hand corner of "grid of grids"  (the default is the lower left hand [lat, lon] of the USA).

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
                            "lower_left": lower_left,
                            "upper_right": upper_right
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



def PointsInCircum(_x,y, r,n=100):
    ret = []
    r = 3*r
    for x in range(0,n+1):
        ret.append(
            (
                _x+float(math.cos(2*pi/n*x)*r),
                y+float(math.sin(2*pi/n*x)*r)
            )
        )
    return ret 

def all_grid(grids, centers):
    """
    Assign prob to all the grids
    """
    for grid in grids:
        _points = grid["features"][0]["geometry"]["coordinates"][0][:-1]
        xx, yy = zip(*_points)
        centroid = (sum(xx) / len(_points), sum(yy) / len(_points))
        temp =  assign_prob(centroid, centers)
        grid["prob_dist"] = sum(temp)
    return grids

def assign_prob(centroid, centers):
    """
    Assign probability of the `point` by comparing the distance with the centers
    """
    prob = []
    for center in centers:
        distance = cal_dist(*centroid, *center["center"])
        strip_no = check_range(distance, center["radius"])
        if strip_no is not None:
            prob.append(center["trust"] * center["strip"][strip_no])
    return prob


def check_range(distance, radius):
    """
    Check in which range of the radius does the distance lie in
    """
    if distance < radius:
        prob = 0
    elif distance > radius and distance < 2*radius:
        prob = 1
    elif distance > 2* radius and distance < 3*radius:
        prob = 2
    else:
        prob = None
    return prob

def cal_dist(x1, y1, x2, y2):
    """
    Calculate the distance between the two points
    """
    return math.hypot(x2-x1, y2-y1)


# def maper():
#     m = folium.Map(location=points[0], zoom_start=3, tiles="CartoDB dark_matter")
#     points = []
#     x, y = circle["center"]
#     x, y = [29.961264, 76.826217]
#     points.extend(PointsInCircum(x, y, circle['radius']*0.0015, n=1000))
#     folium.PolyLine(points).add_to(m)

import math
import numpy as np

def distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
            math.sin(dlat / 2) **2  +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) **2 
         )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

def displace(lat, lng, theta, distance):
    """
    Displace a LatLng theta degrees counterclockwise and some
    meters in that direction.
    Notes:
        http://www.movable-type.co.uk/scripts/latlong.html
        0 DEGREES IS THE VERTICAL Y AXIS! IMPORTANT!
    Args:
        theta:    A number in degrees.
        distance: A number in meters.
    Returns:
        A new LatLng.
    """
    theta = np.float32(theta)

    delta = np.divide(np.float32(distance), np.float32(6471))

    def to_radians(theta):
        return np.divide(np.dot(theta, np.pi), np.float32(180.0))

    def to_degrees(theta):
        return np.divide(np.dot(theta, np.float32(180.0)), np.pi)

    theta = to_radians(theta)
    lat1 = to_radians(lat)
    lng1 = to_radians(lng)

    lat2 = np.arcsin( np.sin(lat1) * np.cos(delta) +
                        np.cos(lat1) * np.sin(delta) * np.cos(theta) )

    lng2 = lng1 + np.arctan2( np.sin(theta) * np.sin(delta) * np.cos(lat1),
                                np.cos(delta) - np.sin(lat1) * np.sin(lat2))

    lng2 = (lng2 + 3 * np.pi) % (2 * np.pi) - np.pi

    return to_degrees(lat2), to_degrees(lng2)
 
def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))