from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)


def get_weather_icon(code):

    if code == 0:
        return "☀️"

    elif code in [1, 2, 3]:
        return "🌤️"

    elif code in [45, 48]:
        return "🌫️"

    elif 51 <= code <= 57:
        return "🌦️"

    elif 61 <= code <= 67:
        return "🌧️"

    elif 71 <= code <= 77:
        return "❄️"

    elif 80 <= code <= 82:
        return "🌦️"

    elif code >= 95:
        return "⛈️"

    return "🌤️"


def get_weather_condition(code):

    if code == 0:
        return "Clear Sky"

    elif code in [1, 2, 3]:
        return "Partly Cloudy"

    elif code in [45, 48]:
        return "Foggy"

    elif 51 <= code <= 57:
        return "Drizzle"

    elif 61 <= code <= 67:
        return "Rain"

    elif 71 <= code <= 77:
        return "Snow"

    elif 80 <= code <= 82:
        return "Rain Showers"

    elif code >= 95:
        return "Thunderstorm"

    return "Unknown"


@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."

        else:

            try:

                # Find city coordinates
                location_response = requests.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={
                        "name": city,
                        "count": 1,
                        "language": "en",
                        "format": "json"
                    },
                    timeout=10
                )

                location_data = location_response.json()

                if not location_data.get("results"):
                    error = "City not found."

                else:

                    location = location_data["results"][0]

                    latitude = location["latitude"]
                    longitude = location["longitude"]

                    # Get weather data
                    weather_response = requests.get(
                        "https://api.open-meteo.com/v1/forecast",
                        params={
                            "latitude": latitude,
                            "longitude": longitude,
                            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                            "timezone": "auto"
                        },
                        timeout=10
                    )

                    weather_data = weather_response.json()

                    current = weather_data["current"]
                    daily = weather_data["daily"]

                    forecast = []

                    for i in range(7):

                        forecast.append({
                           "day": datetime.strptime(
                                daily["time"][i], "%Y-%m-%d"
                            ).strftime("%a"),
                            "icon": get_weather_icon(
                                daily["weather_code"][i]
                            ),
                            "max": round(
                                daily["temperature_2m_max"][i]
                            ),
                            "min": round(
                                daily["temperature_2m_min"][i]
                            )
                        })

                    weather = {
                        "city": location["name"],
                        "temperature": round(
                            current["temperature_2m"]
                        ),
                        "humidity": current[
                            "relative_humidity_2m"
                        ],
                        "wind": round(
                            current["wind_speed_10m"]
                        ),
                        "condition": get_weather_condition(
                            current["weather_code"]
                        ),
                        "icon": get_weather_icon(
                            current["weather_code"]
                        ),
                        "forecast": forecast
                    }

            except Exception as e:

                print("Error:", e)

                error = (
                    "Unable to fetch weather data. "
                    "Please try again."
                )

    return render_template(
        "index.html",
        weather=weather,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)