from flask import Flask, jsonify, Blueprint
from src.weather_today import WeatherPab_today

app = Flask(__name__)

weather_bp = Blueprint('weather', __name__)

class GetWeather:
    def __init__(self):
        self.weather = WeatherPab_today().analysis_data()

    def get_weather(self):
        return self.weather

# 实例化 GetWeather 类
get_weather_instance = GetWeather()

@weather_bp.route('/weather', methods=['GET'])
def weather():
    try:
        weather_data = get_weather_instance.get_weather()
        return jsonify({'weather': weather_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run():
    pass
