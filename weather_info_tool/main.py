# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class WeatherInfoTool(BaseTool):
    """
    A tool to get real-time weather information for a city.

    Args:
        query (dict): A dictionary containing query parameters with the following keys:
            - city (str): The name of the city to get weather information for
            - units (str, optional): The unit system to use for temperature (metric, imperial, standard). Default is metric.
            - include_forecast (bool, optional): Whether to include forecast data. Default is False.

    Returns:
        dict: A dictionary containing weather information including:
            - current_weather: Current weather conditions
            - temperature: Current temperature
            - feels_like: What the temperature feels like
            - humidity: Current humidity percentage
            - wind_speed: Current wind speed
            - description: Text description of weather conditions
            - location: City and country information
            - forecast: Weather forecast data (if requested)
    """

    def get_weather(self, query: dict):
        try:
            # Extract parameters
            city = query.get('city')
            units = query.get('units', 'metric')
            include_forecast = query.get('include_forecast', False)
            
            # Validate inputs
            if not city:
                return "Error: City name is required"
            
            # API key should be stored in environment variables in production
            api_key = os.environ.get('OPENWEATHER_API_KEY', 'your_api_key_here')
            
            # Build API URL for current weather
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': units
            }
            
            # Make API request for current weather
            response = requests.get(base_url, params=params)
            
            # Check if request was successful
            if response.status_code != 200:
                error_message = response.json().get('message', 'Unknown error')
                return f"Error: {error_message} (Status code: {response.status_code})"
            
            # Parse response
            weather_data = response.json()
            
            # Extract relevant information
            result = {
                'current_weather': {
                    'temperature': weather_data['main']['temp'],
                    'feels_like': weather_data['main']['feels_like'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'wind_speed': weather_data['wind']['speed'],
                    'description': weather_data['weather'][0]['description'],
                    'main': weather_data['weather'][0]['main'],
                    'icon': weather_data['weather'][0]['icon'],
                },
                'location': {
                    'city': weather_data['name'],
                    'country': weather_data['sys']['country'],
                    'coordinates': {
                        'lat': weather_data['coord']['lat'],
                        'lon': weather_data['coord']['lon']
                    }
                },
                'timestamp': datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                'units': units
            }
            
            # Add forecast data if requested
            if include_forecast:
                forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
                forecast_params = {
                    'q': city,
                    'appid': api_key,
                    'units': units
                }
                
                forecast_response = requests.get(forecast_url, params=forecast_params)
                
                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    
                    # Process forecast data (typically comes in 3-hour intervals)
                    forecast_list = []
                    for item in forecast_data['list']:
                        forecast_list.append({
                            'timestamp': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                            'temperature': item['main']['temp'],
                            'feels_like': item['main']['feels_like'],
                            'description': item['weather'][0]['description'],
                            'main': item['weather'][0]['main'],
                            'icon': item['weather'][0]['icon'],
                            'humidity': item['main']['humidity'],
                            'wind_speed': item['wind']['speed']
                        })
                    
                    result['forecast'] = forecast_list
                else:
                    result['forecast_error'] = "Could not retrieve forecast data"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in WeatherInfoTool: {e}", exc_info=True)
            return f"Error: {e}"