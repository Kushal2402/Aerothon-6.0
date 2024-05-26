from flask import Flask, request, jsonify, send_from_directory
import psycopg2
import os

app = Flask(__name__)

# Function to connect to the PostgreSQL database
def connect_to_database():
    conn = psycopg2.connect(
        dbname="flight_navigation",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    return conn

# Function to execute a query and fetch weather data based on latitude and longitude
def get_weather_data(latitude, longitude):
    conn = connect_to_database()
    cursor = conn.cursor()

    # Execute the query to fetch weather data based on latitude and longitude
    query = """
    SELECT temperature_2m, relative_humidity_2m, precipitation, rain, snowfall, cloud_cover, pressure_msl, 
           surface_pressure, wind_speed_10m, wind_direction_10m, wind_gusts_10m 
    FROM current_weather 
    WHERE latitude = %s AND longitude = %s
    """
    cursor.execute(query, (latitude, longitude))
    weather_data = cursor.fetchone()

    conn.close()

    if not weather_data:
        return None

    # Convert the fetched data into a dictionary for easier processing
    weather_data_dict = {
        "temperature_2m": weather_data[0],
        "relative_humidity_2m": weather_data[1],
        "precipitation": weather_data[2],
        "rain": weather_data[3],
        "snowfall": weather_data[4],
        "cloud_cover": weather_data[5],
        "pressure_msl": weather_data[6],
        "surface_pressure": weather_data[7],
        "wind_speed_10m": weather_data[8],
        "wind_direction_10m": weather_data[9],
        "wind_gusts_10m": weather_data[10]
    }
    #print(weather_data_dict)
    return weather_data_dict

# Function to calculate risk assessment based on weather parameters and thresholds
def calculate_risk_assessment(weather_data):
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

    risk_assessment = 0
    for param, value in weather_data.items():
        if value < thresholds[param]["low"]:
            risk_assessment += 1
        elif value < thresholds[param]["medium"]:
            risk_assessment += 2
        else:
            risk_assessment += 3

    return risk_assessment

# Function to assign risk level based on risk assessment score
def assign_risk_level(risk_assessment):
    low_threshold = 20  # Example threshold values, adjust according to your requirements
    medium_threshold = 40

    if risk_assessment < low_threshold:
        return "Low"
    elif risk_assessment < medium_threshold:
        return "Medium"
    else:
        return "High"

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/risk_assessment', methods=['POST'])
def get_risk_assessment():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    weather_data = get_weather_data(latitude, longitude)
    if weather_data is None:
        return jsonify({"error": "No weather data found for the provided latitude and longitude"}), 404

    risk_assessment = calculate_risk_assessment(weather_data)
    risk_level = assign_risk_level(risk_assessment)

    return jsonify({"risk_level": risk_level, "weather_data": weather_data})


if __name__ == '__main__':
    app.run(debug=True)
