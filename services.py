from abc import ABC

import requests
from requests import HTTPError


class WeatherFetchingService(ABC):
    @staticmethod
    def get_weather(location):
        raise NotImplementedError


class OpenWeatherMapFetchingService(WeatherFetchingService):
    @staticmethod
    def get_weather(location):
        try:
            response = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + location + "&APPID="
                                    + "b5e4c2506325f2bf4e4a1137c9745969")
            response.raise_for_status()

            return str(response.json()["main"]["temp"])

        except (HTTPError, KeyError):
            return "Unknown"
