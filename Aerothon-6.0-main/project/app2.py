from flask import Flask, render_template, request
import requests
from itertools import permutations
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

thresholds = {
    "temperature_2m": {"low": 10, "medium": 20, "high": 30},
    "relative_humidity_2m": {"low": 30, "medium": 60, "high": 90},
    "precipitation": {"low": 0.1, "medium": 1, "high": 5},
    "rain": {"low": 0.1, "medium": 1, "high": 5},
    "snowfall": {"low": 1, "medium": 5, "high": 10},
    "cloud_cover": {"low": 0.1, "medium": 0.5, "high": 0.8},
    "pressure_msl": {"low": 980, "medium": 1000, "high": 1020},
    "surface_pressure": {"low": 980, "medium": 1000, "high": 1020},
    "wind_speed_10m": {"low": 5, "medium": 10, "high": 20},
    "wind_direction_10m": {"low": 0, "medium": 180, "high": 360},
    "wind_gusts_10m": {"low": 10, "medium": 20, "high": 30}
}

def get_airport_coordinates(code):
    airport_coords = {
        'SFO': (37.7749, -122.4194),
        'DFW': (32.8998, -97.0403),
        'DEN': (39.8561, -104.6737),
        'LAX': (33.9416, -118.4085),
        'ORD': (41.9742, -87.9073)
    }
    return airport_coords.get(code, (0.0, 0.0))

def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = radians(float(coord1[0])), radians(float(coord1[1]))
    lat2, lon2 = radians(float(coord2[0])), radians(float(coord2[1]))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calculate_total_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += haversine(route[i], route[i + 1])
    return total_distance

def find_all_routes(start, end, waypoints):
    all_routes = []
    for perm in permutations(waypoints):
        route = [start] + list(perm) + [end]
        total_distance = calculate_total_distance(route)
        all_routes.append((route, total_distance))
    return sorted(all_routes, key=lambda x: x[1])

def get_weather_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        current_weather = data.get('current_weather', {})
        return current_weather
    else:
        return None

def categorize_weather(weather_data, thresholds):
    categories = {}
    for key, value in weather_data.items():
        if key in thresholds:
            if thresholds[key]["low"] <= value <= thresholds[key]["medium"]:
                categories[key] = "Fair"
            elif value > thresholds[key]["medium"]:
                categories[key] = "Danger"
            else:
                categories[key] = "Good"
    return categories

@app.route('/', methods=['GET', 'POST'])
def index():
    route_info = None
    weather_info_start = None
    weather_info_end = None
    if request.method == 'POST':
        departure = request.form['departure']
        arrival = request.form['arrival']
        waypoint_str = request.form['waypoints'].replace('\r', '').replace(' ', ',')
        waypoints = [tuple(map(float, wp.split(','))) for wp in waypoint_str.split('\n') if wp.strip()]
        start = get_airport_coordinates(departure)
        end = get_airport_coordinates(arrival)
        routes = find_all_routes(start, end, waypoints)
        route_info = []
        for route, distance in routes:
            route_info.append({'route': route, 'distance': distance})
        if start and end:
            weather_info_start = get_weather_data(start[0], start[1])
            weather_info_end = get_weather_data(end[0], end[1])
            weather_info_start = categorize_weather(weather_info_start, thresholds) if weather_info_start else {}
            weather_info_end = categorize_weather(weather_info_end, thresholds) if weather_info_end else {}
    return render_template('index1.html', route_info=route_info, 
                           weather_info_start=weather_info_start, 
                           weather_info_end=weather_info_end)

if __name__ == "__main__":
    app.run(debug=True)
