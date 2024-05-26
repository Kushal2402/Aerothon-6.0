# Flight Navigation System

## Overview

This project provides a comprehensive solution for enhancing flight navigation mechanisms to ensure safe and efficient route planning while mitigating risks.

## Features

- Collects real-time weather and flight data
- Identifies potential risks and scenarios
- Implements optimal route planning algorithm
- Provides a user-friendly dashboard for real-time updates

## Setup

### Prerequisites

- Python 3.x
- SQLite
- Flask

### Installation

1. Clone the repository:
    sh
    git clone https://github.com/yourusername/flight-navigation-system.git
    cd flight-navigation-system
    

2. Install required Python packages:
    sh
    pip install -r requirements.txt
    

3. Set up the database:
    sh
    python collect_data.py
    

4. Run the Flask application:
    sh
    python app.py
    

5. Open your web browser and navigate to http://127.0.0.1:5000 to view the dashboard.

## Usage

- The dashboard displays real-time weather and flight data.
- It highlights potential risks and suggests optimal flight routes.

## API Documentation

- GET /weather_data: Fetches weather data
- GET /flight_data: Fetches flight data

## License

This project is licensed under the MIT License.
