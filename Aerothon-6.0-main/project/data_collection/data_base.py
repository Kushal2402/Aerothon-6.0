import requests
import psycopg2
from psycopg2.extras import execute_values

# Step 1: Fetch data from the API
api_url = "http://api.aviationstack.com/v1/flights?access_key=2dd1322637ebf1467e5f98c94afc4d3c"  # Replace with your actual API endpoint
response = requests.get(api_url)
data = response.json()

# Step 2: Define the database connection
conn = psycopg2.connect(
    dbname="flight_navigation",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

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

# Step 5: Prepare data for insertion
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

# Step 6: Define and execute the SQL query to insert data into the database
query = f"INSERT INTO flight_data ({', '.join(columns)}) VALUES %s"

with conn:
    with conn.cursor() as cur:
        execute_values(cur, query, values)
        conn.commit()

print("Data inserted successfully")
