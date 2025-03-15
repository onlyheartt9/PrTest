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
                "temp_min": 14.44,
                "temp_max": 16.11,
                "pressure": 1024,
                "humidity": 77
            },
            "visibility": 10000,
            "wind": {"speed": 3.09, "deg": 240},
            "clouds": {"all": 0},
            "dt": 1617979425,
            "sys": {
                "type": 1,
                "id": 1414,
                "country": "GB",
                "sunrise": 1617941871,
                "sunset": 1617991012
            },
            "timezone": 3600,
            "id": 2643743,
            "name": "London",
            "cod": 200
        }
        
        self.forecast_response = {
            "cod": "200",
            "message": 0,
            "cnt": 40,
            "list": [
                {
                    "dt": 1617980400,
                    "main": {
                        "temp": 15.5,
                        "feels_like": 14.8,
                        "temp_min": 14.44,
                        "temp_max": 16.11,
                        "pressure": 1024,
                        "humidity": 77
                    },
                    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
                    "clouds": {"all": 0},
                    "wind": {"speed": 3.09, "deg": 240},
                    "visibility": 10000,
                    "pop": 0,
                    "sys": {"pod": "d"},
                    "dt_txt": "2021-04-09 15:00:00"
                }
            ],
            "city": {
                "id": 2643743,
                "name": "London",
                "coord": {"lat": 51.5085, "lon": -0.1257},
                "country": "GB",
                "population": 1000000,
                "timezone": 3600,
                "sunrise": 1617941871,
                "sunset": 1617991012
            }
        }

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_basic(self, mock_get):
        # Test case 1: Basic weather request with valid city
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.current_weather_response
        mock_get.return_value = mock_response
        
        result = self.weather_tool.get_weather({'city': 'London'})
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['q'], 'London')
        self.assertEqual(kwargs['params']['units'], 'metric')
        
        # Verify the result structure and content
        self.assertIn('current_weather', result)
        self.assertIn('location', result)
        self.assertEqual(result['current_weather']['temperature'], 15.5)
        self.assertEqual(result['location']['city'], 'London')
        self.assertEqual(result['location']['country'], 'GB')
        self.assertEqual(result['units'], 'metric')

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_with_units(self, mock_get):
        # Test case 2: Weather request with imperial units
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.current_weather_response
        mock_get.return_value = mock_response
        
        result = self.weather_tool.get_weather({'city': 'London', 'units': 'imperial'})
        
        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['units'], 'imperial')
        self.assertEqual(result['units'], 'imperial')

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_with_forecast(self, mock_get):
        # Test case 3: Weather request with forecast data
        # First response for current weather
        mock_current_response = MagicMock()
        mock_current_response.status_code = 200
        mock_current_response.json.return_value = self.current_weather_response
        
        # Second response for forecast
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = self.forecast_response
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [mock_current_response, mock_forecast_response]
        
        result = self.weather_tool.get_weather({
            'city': 'London', 
            'include_forecast': True
        })
        
        # Verify both APIs were called
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify forecast data is included in the result
        self.assertIn('forecast', result)
        self.assertIsInstance(result['forecast'], list)
        self.assertEqual(len(result['forecast']), 1)  # Based on our mock data
        self.assertIn('temperature', result['forecast'][0])
        self.assertIn('description', result['forecast'][0])

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_missing_city(self, mock_get):
        # Test case 4: Missing city parameter
        result = self.weather_tool.get_weather({})
        
        # Verify the API was not called
        mock_get.assert_not_called()
        
        # Verify error message
        self.assertEqual(result, "Error: City name is required")

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_api_error(self, mock_get):
        # Test case 5: API returns an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "City not found"}
        mock_get.return_value = mock_response
        
        result = self.weather_tool.get_weather({'city': 'NonExistentCity'})
        
        # Verify error handling
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("City not found", result)
        self.assertIn("404", result)

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_exception_handling(self, mock_get):
        # Test case 6: Exception during API call
        mock_get.side_effect = Exception("Network error")
        
        result = self.weather_tool.get_weather({'city': 'London'})
        
        # Verify exception handling
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Network error", result)

    @patch('engine.tools.weather_info_tool.requests.get')
    def test_get_weather_forecast_error(self, mock_get):
        # Test case 7: Current weather succeeds but forecast fails
        # First response for current weather
        mock_current_response = MagicMock()
        mock_current_response.status_code = 200
        mock_current_response.json.return_value = self.current_weather_response
        
        # Second response for forecast (error)
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 500
        mock_forecast_response.json.return_value = {"message": "Internal server error"}
        
        # Configure mock to return different responses
        mock_get.side_effect = [mock_current_response, mock_forecast_response]
        
        result = self.weather_tool.get_weather({
            'city': 'London', 
            'include_forecast': True
        })
        
        # Verify both APIs were called
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify current weather data is included
        self.assertIn('current_weather', result)
        
        # Verify forecast error is included
        self.assertIn('forecast_error', result)
        self.assertEqual(result['forecast_error'], "Could not retrieve forecast data")

if __name__ == '__main__':
    unittest.main()