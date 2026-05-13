import json
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


HERE = Path(__file__).resolve().parent
TEMPLATES = {
    "selection": HERE / "weather_selection.html",
    "result": HERE / "weather_result.html",
}


CITIES = {
    "Jerusalem": (31.7683, 35.2137),
    "New York": (40.7128, -74.0060),
    "Bangkok": (13.7563, 100.5018),
}


def fetch_open_meteo(latitude: float, longitude: float, timezone_name: str = "auto") -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relativehumidity_2m",
        "current_weather": "true",
        "timezone": timezone_name,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8")

    return json.loads(data)


def extract_temperature_humidity(weather_data: dict) -> tuple[float, float, str]:
    current_weather = weather_data.get("current_weather", {})
    hourly = weather_data.get("hourly", {})
    hourly_times = hourly.get("time", [])
    humidity_values = hourly.get("relativehumidity_2m", [])

    if current_weather:
        temperature = current_weather.get("temperature")
        current_time = current_weather.get("time")
    else:
        temperature = None
        current_time = None

    humidity = None
    if current_time and current_time in hourly_times:
        index = hourly_times.index(current_time)
        if index < len(humidity_values):
            humidity = humidity_values[index]

    if humidity is None and humidity_values:
        humidity = humidity_values[0]

    if temperature is None and "temperature_2m" in hourly:
        temperature_values = hourly.get("temperature_2m", [])
        if hourly_times and temperature_values:
            temperature = temperature_values[0]
            current_time = hourly_times[0]

    if temperature is None or humidity is None or current_time is None:
        raise ValueError("Unable to extract temperature and humidity from Open-Meteo response.")

    return temperature, humidity, current_time


def format_weather_report(city_name: str, latitude: float, longitude: float, temperature: float, humidity: float, observation_time: str) -> str:
    report_lines = [
        f"Weather for {city_name}",
        f"Coordinates: {latitude:.4f}, {longitude:.4f}",
        f"Observation time: {observation_time}",
        f"Temperature: {temperature:.1f} °C",
        f"Humidity: {humidity:.1f} %",
    ]
    return "\n".join(report_lines)


def load_template(template_name: str) -> str:
    template_path = TEMPLATES.get(template_name)
    if not template_path or not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return template_path.read_text(encoding="utf-8")


def build_selection_page() -> str:
    options = "\n".join(
        f'<option value="{urllib.parse.quote(city)}">{city}</option>'
        for city in CITIES
    )
    template = load_template("selection")
    return template.replace("{options}", options)


def build_result_page(city_name: str, report_text: str, error: str | None = None) -> str:
    result_html = f"<pre class='bg-light p-3 rounded'>{report_text}</pre>" if not error else f"<div class='alert alert-danger'>{error}</div>"
    template = load_template("result")
    return template.format(city_name=city_name, result_html=result_html)


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/":
            self.respond_html(build_selection_page())
            return

        if parsed_url.path == "/weather":
            query = urllib.parse.parse_qs(parsed_url.query)
            city = query.get("city", [""])[0]
            city = urllib.parse.unquote(city)

            if city not in CITIES:
                self.respond_json({"error": "City selection is invalid."}, status_code=400)
                return

            latitude, longitude = CITIES[city]
            try:
                weather_data = fetch_open_meteo(latitude, longitude)
                temperature, humidity, observation_time = extract_temperature_humidity(weather_data)
                self.respond_json({
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "temperature": temperature,
                    "humidity": humidity,
                    "observation_time": observation_time,
                })
            except Exception as exc:
                self.respond_json({"error": str(exc)}, status_code=500)
            return

        self.send_error(404, "Not Found")

    def respond_json(self, payload: dict, status_code: int = 200) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def respond_html(self, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    server_address = ("localhost", 8000)
    print("Starting Open-Meteo web server on http://localhost:8000")
    print("Open that address in your browser and choose Jerusalem, New York, or Bangkok.")
    httpd = HTTPServer(server_address, WeatherHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
