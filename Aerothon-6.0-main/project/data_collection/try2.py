import openmeteo_requests
import requests_cache
from retry_requests import retry
import psycopg2
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 32.8998,
    "longitude": -97.0403,
    "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_precipitation = current.Variables(2).Value()
current_rain = current.Variables(3).Value()
current_snowfall = current.Variables(4).Value()
current_cloud_cover = current.Variables(5).Value()
current_pressure_msl = current.Variables(6).Value()
current_surface_pressure = current.Variables(7).Value()
current_wind_speed_10m = current.Variables(8).Value()
current_wind_direction_10m = current.Variables(9).Value()
current_wind_gusts_10m = current.Variables(10).Value()

# Convert Unix timestamp to datetime
current_time = datetime.fromtimestamp(current.Time())

# Retrieve latitude and longitude from the response
latitude = params['latitude']
longitude = params['longitude']

# Database connection and table creation in PostgreSQL
conn = psycopg2.connect(
    dbname="flight_navigation",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
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
    wind_gusts_10m REAL
)
''')

# Insert the current weather data
cursor.execute('''
INSERT INTO current_weather (time, latitude, longitude, temperature_2m, relative_humidity_2m, precipitation, rain, snowfall, cloud_cover, pressure_msl, surface_pressure, wind_speed_10m, wind_direction_10m, wind_gusts_10m)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
''', (
    current_time,
    latitude,
    longitude,
    current_temperature_2m,
    current_relative_humidity_2m,
    current_precipitation,
    current_rain,
    current_snowfall,
    current_cloud_cover,
    current_pressure_msl,
    current_surface_pressure,
    current_wind_speed_10m,
    current_wind_direction_10m,
    current_wind_gusts_10m
))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data stored in PostgreSQL database successfully")
