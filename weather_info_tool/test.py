import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
from datetime import datetime

# Import the module containing the function to be tested
# Assuming the WeatherInfoTool is in a file called weather_info_tool.py
# in a directory structure that matches the import path in the original code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from engine.tools.weather_info_tool import WeatherInfoTool

class TestWeatherInfoTool(unittest.TestCase):
    def setUp(self):
        self.weather_tool = WeatherInfoTool()
        # Sample response data for mocking
        self.current_weather_response = {
            "coord": {"lon": -0.1257, "lat": 51.5085},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
            "base": "stations",
            "main": {
                "temp": 15.5,
                "feels_like": 14.8,
                "temp_min": 14.2,
                "temp_max": 16.7,
                "pressure": 1023,
                "humidity": 76
            },
            "visibility": 10000,
            "wind": {"speed": 3.6, "deg": 250},
            "clouds": {"all": 0},
            "dt": 1619352000,
            "sys": {
                "type": 2,
                "id": 2019646,
                "country": "GB",
                "sunrise": 1619325935,
                "sunset": 1619378329
            },
            "timezone": 3600,
            "id": 2643743,
            "name": "London",
            "cod": 200
        }
        
        self.forecast_response = {
            "cod": "200",
            "message": 0,
            "cnt": 2,
            "list": [
                {
                    "dt": 1619352000,
                    "main": {
                        "temp": 15.5,
                        "feels_like": 14.8,
                        "temp_min": 14.2,
                        "temp_max": 16.7,
                        "pressure": 1023,
                        "humidity": 76
                    },
                    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
                    "clouds": {"all": 0},
                    "wind": {"speed": 3.6, "deg": 250},
                    "visibility": 10000,
                    "pop": 0,
                    "sys": {"pod": "d"},
                    "dt_txt": "2021-04-25 12:00:00"
                },
                {
                    "dt": 1619362800,
                    "main": {
                        "temp": 14.2,
                        "feels_like": 13.5,
                        "temp_min": 13.1,
                        "temp_max": 14.2,
                        "pressure": 1023,
                        "humidity": 82
                    },
                    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}],
                    "clouds": {"all": 0},
                    "wind": {"speed": 2.8, "deg": 240},
                    "visibility": 10000,
                    "pop": 0,
                    "sys": {"pod": "n"},
                    "dt_txt": "2021-04-25 15:00:00"
                }
            ],
            "city": {
                "id": 2643743,
                "name": "London",
                "coord": {"lat": 51.5085, "lon": -0.1257},
                "country": "GB",
                "population": 1000000,
                "timezone": 3600,
                "sunrise": 1619325935,
                "sunset": 1619378329
            }
        }

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_basic(self, mock_get):
        # Test case 1: Basic weather request without forecast
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.current_weather_response
        mock_get.return_value = mock_response
        
        result = self.weather_tool.get_weather({'city': 'London'})
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather", 
            params={'q': 'London', 'appid': 'test_api_key', 'units': 'metric'}
        )
        
        # Verify the result structure and content
        self.assertEqual(result['current_weather']['temperature'], 15.5)
        self.assertEqual(result['current_weather']['feels_like'], 14.8)
        self.assertEqual(result['current_weather']['humidity'], 76)
        self.assertEqual(result['current_weather']['description'], 'clear sky')
        self.assertEqual(result['location']['city'], 'London')
        self.assertEqual(result['location']['country'], 'GB')
        self.assertEqual(result['units'], 'metric')
        self.assertNotIn('forecast', result)

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_with_forecast(self, mock_get):
        # Test case 2: Weather request with forecast
        # Set up mock for current weather
        mock_current_response = MagicMock()
        mock_current_response.status_code = 200
        mock_current_response.json.return_value = self.current_weather_response
        
        # Set up mock for forecast
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = self.forecast_response
        
        # Configure the mock to return different responses for different calls
        mock_get.side_effect = [mock_current_response, mock_forecast_response]
        
        result = self.weather_tool.get_weather({
            'city': 'London', 
            'units': 'imperial', 
            'include_forecast': True
        })
        
        # Verify both API calls were made with correct parameters
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(
            "https://api.openweathermap.org/data/2.5/weather", 
            params={'q': 'London', 'appid': 'test_api_key', 'units': 'imperial'}
        )
        mock_get.assert_any_call(
            "https://api.openweathermap.org/data/2.5/forecast", 
            params={'q': 'London', 'appid': 'test_api_key', 'units': 'imperial'}
        )
        
        # Verify the result includes forecast data
        self.assertIn('forecast', result)
        self.assertEqual(len(result['forecast']), 2)
        self.assertEqual(result['forecast'][0]['temperature'], 15.5)
        self.assertEqual(result['forecast'][1]['temperature'], 14.2)
        self.assertEqual(result['units'], 'imperial')

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_api_error(self, mock_get):
        # Test case 3: API returns an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "City not found"}
        mock_get.return_value = mock_response
        
        result = self.weather_tool.get_weather({'city': 'NonExistentCity'})
        
        # Verify the error is properly handled
        self.assertTrue(isinstance(result, str))
        self.assertIn("Error:", result)
        self.assertIn("City not found", result)
        self.assertIn("404", result)

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_missing_city(self, mock_get):
        # Test case 4: Missing city parameter
        result = self.weather_tool.get_weather({})
        
        # Verify the error is properly handled
        self.assertEqual(result, "Error: City name is required")
        # Ensure the API was not called
        mock_get.assert_not_called()

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_forecast_api_error(self, mock_get):
        # Test case 5: Current weather succeeds but forecast fails
        # Set up mock for current weather
        mock_current_response = MagicMock()
        mock_current_response.status_code = 200
        mock_current_response.json.return_value = self.current_weather_response
        
        # Set up mock for forecast (error)
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 500
        mock_forecast_response.json.return_value = {"message": "Internal server error"}
        
        # Configure the mock to return different responses for different calls
        mock_get.side_effect = [mock_current_response, mock_forecast_response]
        
        result = self.weather_tool.get_weather({
            'city': 'London', 
            'include_forecast': True
        })
        
        # Verify both API calls were made
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify the result has current weather but indicates forecast error
        self.assertIn('current_weather', result)
        self.assertIn('forecast_error', result)
        self.assertEqual(result['forecast_error'], "Could not retrieve forecast data")

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_exception_handling(self, mock_get):
        # Test case 6: Exception during API call
        mock_get.side_effect = Exception("Network error")
        
        result = self.weather_tool.get_weather({'city': 'London'})
        
        # Verify the exception is properly handled
        self.assertTrue(isinstance(result, str))
        self.assertIn("Error:", result)
        self.assertIn("Network error", result)

    @patch('engine.tools.weather_info_tool.requests.get')
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_api_key"})
    def test_get_weather_different_units(self, mock_get):
        # Test case 7: Test with different units
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.current_weather_response
        mock_get.return_value = mock_response
        
        # Test with standard units
        self.weather_tool.get_weather({'city': 'London', 'units': 'standard'})
        
        # Verify the API was called with correct units
        mock_get.assert_called_with(
            "https://api.openweathermap.org/data/2.5/weather", 
            params={'q': 'London', 'appid': 'test_api_key', 'units': 'standard'}
        )

if __name__ == '__main__':
    unittest.main()