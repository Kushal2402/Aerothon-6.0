import requests
from itertools import permutations
from math import radians, sin, cos, sqrt, atan2

thresholds = {
    "temperature_2m": {"low": 10, "medium": 20, "high": 30},
    "relative_humidity_2m": {"low": 30, "medium": 60, "high": 90},
    "precipitation": {"low": 0.1, "medium": 1, "high": 5},  # in mm/hr
    "rain": {"low": 0.1, "medium": 1, "high": 5},  # in mm/hr
    "snowfall": {"low": 1, "medium": 5, "high": 10},  # in mm/hr
    "cloud_cover": {"low": 0.1, "medium": 0.5, "high": 0.8},
    "pressure_msl": {"low": 980, "medium": 1000, "high": 1020},  # in hPa
    "surface_pressure": {"low": 980, "medium": 1000, "high": 1020},  # in hPa
    "wind_speed_10m": {"low": 5, "medium": 10, "high": 20},  # in m/s
    "wind_direction_10m": {"low": 0, "medium": 180, "high": 360},  # in degrees
    "wind_gusts_10m": {"low": 10, "medium": 20, "high": 30}  # in m/s
}

# Mock function to convert IATA/ICAO codes to latitude and longitude
def get_airport_coordinates(code):
    airport_coords = {
        'SFO': (37.7749, -122.4194),  # San Francisco
        'DFW': (32.8998, -97.0403),   # Dallas/Fort Worth
        'DEN': (39.8561, -104.6737),  # Denver
        'LAX': (33.9416, -118.4085),  # Los Angeles
        'ORD': (41.9742, -87.9073)    # Chicago O'Hare
    }
    return airport_coords.get(code, (0.0, 0.0))  # Default to (0,0) if not found

# Haversine formula to calculate distance between two points on the Earth
def haversine(coord1, coord2):
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

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
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'current_weather' in data:
            return data['current_weather']
    print("Failed to fetch weather data.")
    return None

def categorize_weather(weather_data, thresholds):
    categories = {}
    for key, value in weather_data.items():
        if key in thresholds:
            if value <= thresholds[key]["low"]:
                categories[key] = "Good"
            elif value <= thresholds[key]["medium"]:
                categories[key] = "Fair"
            else:
                categories[key] = "Danger"
    return categories

def main():
    # Sample data from the API
    api_data = {
        "departure": {
            "airport": "San Francisco International",
            "iata": "SFO",
        },
        "arrival": {
            "airport": "Dallas/Fort Worth International",
            "iata": "DFW",
        }
    }

    # Get coordinates from IATA codes
    start = get_airport_coordinates(api_data["departure"]["iata"])
    end = get_airport_coordinates(api_data["arrival"]["iata"])

    print("Enter the waypoints (latitude longitude), type 'done' to finish:")
    waypoints = []
    while True:
        wp_input = input("Waypoint: ").strip()
        if wp_input.lower() == 'done':
            break
        try:
            lat, lon = map(float, wp_input.split())
            waypoints.append((lat, lon))
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a space or type 'done' to finish.")

    if not waypoints:
        print("No waypoints entered. Exiting.")
        return

    all_routes = find_all_routes(start, end, waypoints)
    print("\nAll Possible Routes in Ascending Order of Total Distance:")
    for route, distance in all_routes:
        print(f"Route: {route} \nTotal Distance: {distance:.2f} km\n")

        # Fetch weather data for start and end points
        start_weather_data = get_weather_data(start[0], start[1])
        end_weather_data = get_weather_data(end[0], end[1])

        if start_weather_data and end_weather_data:
            print("Weather data for departure airport:")
            print(categorize_weather(start_weather_data, thresholds))
            print("Weather data for arrival airport:")
            print(categorize_weather(end_weather_data, thresholds))
        else:
            print("Failed to fetch weather data.")

if __name__ == "__main__":
    main()
