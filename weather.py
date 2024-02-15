import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "eveveveveveveve"
# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = "jxHSRFqicsxrINdmOBTwRQ==R3zoo4FWQILzOghz"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location, date):
    url_base_url = "https://weather.visualcrossing.com"
    mid_url = "VisualCrossingWebServices/rest/services/timeline"
    end_url = "unitGroup=metric&include=days&key=SARW5D67YY588DZSC4V3EVJQL&contentType=json"

    url = f"{url_base_url}/{mid_url}/{location}?{end_url}"

    headers = {"X-Api-Key": RSA_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        response_json = json.loads(response.text)
        days = response_json["days"]
        one_day = [day for day in days if day["datetime"] == date]
        if not one_day:
            raise InvalidUsage("No weather data available for the provided date", status_code=404)
        one_day = one_day[0]
        weather_data = {
            "temperature": one_day["temp"],
            "wind speed": one_day["windspeed"],
            "pressure": one_day["pressure"],
            "humidity": one_day["humidity"],
            "conditions": one_day["conditions"],
            "description": one_day["description"],
        }
        return weather_data
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    requester_name = json_data.get("requester_name")
    token = json_data.get("token")
    timestamp = dt.datetime.utcnow().isoformat()
    location = json_data.get("location")
    date = json_data.get("date")

    if not all([requester_name, token, location, date]):
        raise InvalidUsage("Requester name, token, location, and date are required", status_code=400)

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    try:
        weather = get_weather(location, date)
    except InvalidUsage as e:
        return jsonify(e.to_dict()), e.status_code

    result = {
        "requester_name": requester_name,
        "timestamp": timestamp,
        "location": location,
        "date": date,
        "weather": weather
    }

    return result