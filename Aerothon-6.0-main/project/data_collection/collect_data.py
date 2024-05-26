import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Database connection details
db_params = {
    'dbname': 'flight_navigation',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}

def get_weather_data():
    # Make sure all required weather variables are listed here
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 82.1,
        "longitude": 12.4,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    weather_data = {
        'time': datetime.fromtimestamp(current.Time()),
        'latitude': params['latitude'],
        'longitude': params['longitude'],
        'temperature_2m': current.Variables(0).Value(),
        'relative_humidity_2m': current.Variables(1).Value(),
        'precipitation': current.Variables(2).Value(),
        'rain': current.Variables(3).Value(),
        'snowfall': current.Variables(4).Value(),
        'cloud_cover': current.Variables(5).Value(),
        'pressure_msl': current.Variables(6).Value(),
        'surface_pressure': current.Variables(7).Value(),
        'wind_speed_10m': current.Variables(8).Value(),
        'wind_direction_10m': current.Variables(9).Value(),
        'wind_gusts_10m': current.Variables(10).Value()
    }
    return weather_data

def store_weather_data(weather_data):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    # Create table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS current_weather (
        id SERIAL PRIMARY KEY,
        time TIMESTAMP,
        latitude REAL,
        longitude REAL,
        temperature_2m REAL,
        relative_humidity_2m REAL,
        precipitation REAL,
        rain REAL,
        snowfall REAL,
        cloud_cover REAL,
        pressure_msl REAL,
        surface_pressure REAL,
        wind_speed_10m REAL,
        wind_direction_10m REAL,
        wind_gusts REALpython3 -m venv venv

    )
    ''')

    # Insert the current weather data
    cursor.execute('''
    INSERT INTO current_weather (time, latitude, longitude, temperature_2m, relative_humidity_2m, precipitation, rain, snowfall, cloud_cover, pressure_msl, surface_pressure, wind_speed_10m, wind_direction_10m, wind_gusts)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        weather_data['time'],
        weather_data['latitude'],
        weather_data['longitude'],
        weather_data['temperature_2m'],
        weather_data['relative_humidity_2m'],
        weather_data['precipitation'],
        weather_data['rain'],
        weather_data['snowfall'],
        weather_data['cloud_cover'],
        weather_data['pressure_msl'],
        weather_data['surface_pressure'],
        weather_data['wind_speed_10m'],
        weather_data['wind_direction_10m'],
        weather_data['wind_gusts']
    ))

    conn.commit()
    conn.close()
    print("Weather data stored in PostgreSQL database successfully")

def get_flight_data():
    api_url = "http://api.aviationstack.com/v1/flights?access_key=2dd1322637ebf1467e5f98c94afc4d3c"  # Replace with your actual API endpoint
    response = requests.get(api_url)
    return response.json()

def store_flight_data(data):
    conn = psycopg2.connect(**db_params)
    
    # Step 4: Define the mapping
    field_mapping = {
        "flight_date": "flight_date",
        "flight_status": "flight_status",
        "departure.airport": "departure_airport",
        "departure.timezone": "departure_timezone",
        "departure.iata": "departure_iata",
        "departure.icao": "departure_icao",
        "departure.terminal": "departure_terminal",
        "departure.gate": "departure_gate",
        "departure.delay": "departure_delay",
        "departure.scheduled": "departure_scheduled",
        "departure.estimated": "departure_estimated",
        "departure.actual": "departure_actual",
        "departure.estimated_runway": "departure_estimated_runway",
        "departure.actual_runway": "departure_actual_runway",
        "arrival.airport": "arrival_airport",
        "arrival.timezone": "arrival_timezone",
        "arrival.iata": "arrival_iata",
        "arrival.icao": "arrival_icao",
        "arrival.terminal": "arrival_terminal",
        "arrival.gate": "arrival_gate",
        "arrival.baggage": "arrival_baggage",
        "arrival.delay": "arrival_delay",
        "arrival.scheduled": "arrival_scheduled",
        "arrival.estimated": "arrival_estimated",
        "arrival.actual": "arrival_actual",
        "arrival.estimated_runway": "arrival_estimated_runway",
        "arrival.actual_runway": "arrival_actual_runway",
        "airline.name": "airline_name",
        "airline.iata": "airline_iata",
        "airline.icao": "airline_icao",
        "flight.number": "flight_number",
        "flight.iata": "flight_iata",
        "flight.icao": "flight_icao",
        "aircraft.registration": "aircraft_registration",
        "aircraft.iata": "aircraft_iata",
        "aircraft.icao": "aircraft_icao",
        "aircraft.icao24": "aircraft_icao24",
        "live.updated": "live_updated",
        "live.latitude": "live_latitude",
        "live.longitude": "live_longitude",
        "live.altitude": "live_altitude",
        "live.direction": "live_direction",
        "live.speed_horizontal": "live_speed_horizontal",
        "live.speed_vertical": "live_speed_vertical",
        "live.is_ground": "live_is_ground"
    }

    def flatten(data, parent_key='', sep='.'):
        items = []
        for k, v in data.items():
            new_key = f'{parent_key}{sep}{k}' if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    flattened_data = [flatten(item) for item in data.get('data', [])]

    columns = list(field_mapping.values())
    values = [[item.get(key, None) for key in field_mapping.keys()] for item in flattened_data]

    query = f"INSERT INTO flight_data ({', '.join(columns)}) VALUES %s"

    with conn:
        with conn.cursor() as cur:
            execute_values(cur, query, values)
            conn.commit()

    print("Flight data inserted successfully")

def main():
    # Get and store weather data
    weather_data = get_weather_data()
    store_weather_data(weather_data)

    # Get and store flight data
    flight_data = get_flight_data()
    store_flight_data(flight_data)

if __name__ == "__main__":
    main()
