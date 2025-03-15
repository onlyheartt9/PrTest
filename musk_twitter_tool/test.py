import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime, timedelta

# Import the module containing the function to be tested
# Assuming the MuskTwitterTool is in a file called musk_twitter_tool.py
# in a directory structure that matches the import path in the original code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from engine.tools.social_media.musk_twitter_tool import MuskTwitterTool

class TestMuskTwitterTool(unittest.TestCase):
    def setUp(self):
        self.tool = MuskTwitterTool()
        
    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_SECRET': 'test_token_secret'
    })
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_get_musk_tweets_success(self, mock_api, mock_auth):
        # Setup mock responses
        mock_user = MagicMock()
        mock_user.id_str = '44196397'
        mock_user.name = 'Elon Musk'
        mock_user.screen_name = 'elonmusk'
        mock_user.description = 'Test description'
        mock_user.followers_count = 100000000
        mock_user.friends_count = 100
        mock_user.statuses_count = 10000
        mock_user.profile_image_url_https = 'https://example.com/profile.jpg'
        mock_user.verified = True
        
        mock_tweet1 = MagicMock()
        mock_tweet1.id_str = '123456789'
        mock_tweet1.full_text = 'Test tweet 1'
        mock_tweet1.created_at = datetime.now() - timedelta(hours=1)
        mock_tweet1.retweet_count = 5000
        mock_tweet1.favorite_count = 20000
        mock_tweet1.in_reply_to_status_id = None
        mock_tweet1.retweeted_status = None
        
        mock_tweet2 = MagicMock()
        mock_tweet2.id_str = '987654321'
        mock_tweet2.full_text = 'Test tweet 2'
        mock_tweet2.created_at = datetime.now() - timedelta(hours=2)
        mock_tweet2.retweet_count = 10000
        mock_tweet2.favorite_count = 30000
        mock_tweet2.in_reply_to_status_id = None
        mock_tweet2.retweeted_status = None
        
        # Configure mocks
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_user.return_value = mock_user
        
        # Mock the Cursor functionality
        mock_cursor = MagicMock()
        mock_cursor.items.return_value = [mock_tweet1, mock_tweet2]
        
        with patch('tweepy.Cursor', return_value=mock_cursor):
            # Test with default parameters
            result = self.tool.get_musk_tweets({})
            
            # Verify the result structure
            self.assertIsInstance(result, dict)
            self.assertIn('tweets', result)
            self.assertIn('user_info', result)
            self.assertIn('retrieved_at', result)
            self.assertIn('query_params', result)
            
            # Verify tweets data
            self.assertEqual(len(result['tweets']), 2)
            self.assertEqual(result['tweets'][0]['id'], '123456789')
            self.assertEqual(result['tweets'][0]['text'], 'Test tweet 1')
            self.assertEqual(result['tweets'][1]['id'], '987654321')
            
            # Verify user info
            self.assertEqual(result['user_info']['name'], 'Elon Musk')
            self.assertEqual(result['user_info']['screen_name'], 'elonmusk')
            
            # Verify query params
            self.assertEqual(result['query_params']['count'], 10)
            self.assertEqual(result['query_params']['include_retweets'], False)
            self.assertEqual(result['query_params']['include_replies'], False)
            self.assertEqual(result['query_params']['hours_back'], 24)
    
    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_SECRET': 'test_token_secret'
    })
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_get_musk_tweets_with_custom_params(self, mock_api, mock_auth):
        # Setup mock responses
        mock_user = MagicMock()
        mock_user.id_str = '44196397'
        mock_user.name = 'Elon Musk'
        mock_user.screen_name = 'elonmusk'
        mock_user.description = 'Test description'
        mock_user.followers_count = 100000000
        mock_user.friends_count = 100
        mock_user.statuses_count = 10000
        mock_user.profile_image_url_https = 'https://example.com/profile.jpg'
        mock_user.verified = True
        
        # Create a mix of tweets, retweets and replies
        mock_tweet1 = MagicMock()
        mock_tweet1.id_str = '123456789'
        mock_tweet1.full_text = 'Test tweet 1'
        mock_tweet1.created_at = datetime.now() - timedelta(hours=1)
        mock_tweet1.retweet_count = 5000
        mock_tweet1.favorite_count = 20000
        mock_tweet1.in_reply_to_status_id = None
        # No retweeted_status attribute means it's not a retweet
        
        mock_tweet2 = MagicMock()
        mock_tweet2.id_str = '987654321'
        mock_tweet2.full_text = 'Test tweet 2'
        mock_tweet2.created_at = datetime.now() - timedelta(hours=2)
        mock_tweet2.retweet_count = 10000
        mock_tweet2.favorite_count = 30000
        mock_tweet2.in_reply_to_status_id = '111111'  # This is a reply
        # No retweeted_status attribute
        
        mock_tweet3 = MagicMock()
        mock_tweet3.id_str = '555555555'
        mock_tweet3.full_text = 'Test retweet'
        mock_tweet3.created_at = datetime.now() - timedelta(hours=3)
        mock_tweet3.retweet_count = 7000
        mock_tweet3.favorite_count = 15000
        mock_tweet3.in_reply_to_status_id = None
        mock_tweet3.retweeted_status = MagicMock()  # This makes it a retweet
        
        # Configure mocks
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_user.return_value = mock_user
        
        # Mock the Cursor functionality
        mock_cursor = MagicMock()
        mock_cursor.items.return_value = [mock_tweet1, mock_tweet2, mock_tweet3]
        
        with patch('tweepy.Cursor', return_value=mock_cursor):
            # Test with custom parameters
            query = {
                'count': 5,
                'include_retweets': True,
                'include_replies': True,
                'hours_back': 12
            }
            result = self.tool.get_musk_tweets(query)
            
            # Verify the result structure
            self.assertIsInstance(result, dict)
            self.assertIn('tweets', result)
            
            # Verify query params were used
            self.assertEqual(result['query_params']['count'], 5)
            self.assertEqual(result['query_params']['include_retweets'], True)
            self.assertEqual(result['query_params']['include_replies'], True)
            self.assertEqual(result['query_params']['hours_back'], 12)
    
    def test_get_musk_tweets_missing_credentials(self):
        # Test with missing API credentials
        with patch.dict(os.environ, {}, clear=True):
            result = self.tool.get_musk_tweets({})
            self.assertEqual(result, "Error: Twitter API credentials not found in environment variables")
    
    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_SECRET': 'test_token_secret'
    })
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_get_musk_tweets_api_error(self, mock_api, mock_auth):
        # Setup mock to raise an exception
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_user.side_effect = Exception("API rate limit exceeded")
        
        # Test error handling
        result = self.tool.get_musk_tweets({})
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("API rate limit exceeded", result)
    
    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_SECRET': 'test_token_secret'
    })
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_get_musk_tweets_with_media(self, mock_api, mock_auth):
        # Setup mock responses
        mock_user = MagicMock()
        mock_user.id_str = '44196397'
        mock_user.name = 'Elon Musk'
        mock_user.screen_name = 'elonmusk'
        mock_user.description = 'Test description'
        mock_user.followers_count = 100000000
        mock_user.friends_count = 100
        mock_user.statuses_count = 10000
        mock_user.profile_image_url_https = 'https://example.com/profile.jpg'
        mock_user.verified = True
        
        # Create a tweet with media
        mock_tweet = MagicMock()
        mock_tweet.id_str = '123456789'
        mock_tweet.full_text = 'Test tweet with media'
        mock_tweet.created_at = datetime.now() - timedelta(hours=1)
        mock_tweet.retweet_count = 5000
        mock_tweet.favorite_count = 20000
        mock_tweet.in_reply_to_status_id = None
        
        # Add media to the tweet
        mock_tweet.extended_entities = {
            'media': [
                {
                    'type': 'photo',
                    'media_url_https': 'https://example.com/photo.jpg'
                },
                {
                    'type': 'video',
                    'media_url_https': 'https://example.com/video.mp4'
                }
            ]
        }
        
        # Configure mocks
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_user.return_value = mock_user
        
        # Mock the Cursor functionality
        mock_cursor = MagicMock()
        mock_cursor.items.return_value = [mock_tweet]
        
        with patch('tweepy.Cursor', return_value=mock_cursor):
            result = self.tool.get_musk_tweets({})
            
            # Verify media was included in the result
            self.assertIn('media', result['tweets'][0])
            self.assertEqual(len(result['tweets'][0]['media']), 2)
            self.assertEqual(result['tweets'][0]['media'][0]['type'], 'photo')
            self.assertEqual(result['tweets'][0]['media'][1]['type'], 'video')

if __name__ == '__main__':
    unittest.main()