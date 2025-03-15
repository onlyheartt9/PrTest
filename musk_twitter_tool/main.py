# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import requests
import tweepy
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class MuskTwitterTool(BaseTool):
    """
    A tool to get real-time updates from Elon Musk's Twitter/X account.

    Args:
        query (dict): A dictionary containing query parameters with the following keys:
            - count (int, optional): Number of recent tweets to retrieve. Default is 10.
            - include_retweets (bool, optional): Whether to include retweets. Default is False.
            - include_replies (bool, optional): Whether to include replies. Default is False.
            - hours_back (int, optional): Only retrieve tweets from the last X hours. Default is 24.

    Returns:
        dict: A dictionary containing Elon Musk's recent tweets including:
            - tweets: List of recent tweets with text, created_at, retweet_count, etc.
            - user_info: Basic information about Elon Musk's account
            - retrieved_at: Timestamp when the data was retrieved
    """

    def get_musk_tweets(self, query: dict):
        try:
            # Extract parameters
            count = query.get('count', 10)
            include_retweets = query.get('include_retweets', False)
            include_replies = query.get('include_replies', False)
            hours_back = query.get('hours_back', 24)
            
            # Get API credentials from environment variables
            consumer_key = os.environ.get('TWITTER_API_KEY')
            consumer_secret = os.environ.get('TWITTER_API_SECRET')
            access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.environ.get('TWITTER_ACCESS_SECRET')
            
            # Validate credentials
            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                return "Error: Twitter API credentials not found in environment variables"
            
            # Set up Tweepy client
            auth = tweepy.OAuth1UserHandler(
                consumer_key, consumer_secret, access_token, access_token_secret
            )
            api = tweepy.API(auth)
            
            # Elon Musk's Twitter/X user ID
            musk_user_id = "44196397"  # Elon Musk's Twitter ID
            
            # Get user information
            user = api.get_user(user_id=musk_user_id)
            
            # Calculate time threshold for filtering tweets
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            
            # Get tweets
            tweets_data = []
            
            # Use Tweepy Cursor to handle pagination
            for tweet in tweepy.Cursor(
                api.user_timeline,
                user_id=musk_user_id,
                count=count,
                tweet_mode="extended",
                include_rts=include_retweets
            ).items(count * 2):  # Fetch more than needed to account for filtering
                
                # Skip replies if not requested
                if not include_replies and tweet.in_reply_to_status_id is not None:
                    continue
                
                # Check if tweet is within the time threshold
                if tweet.created_at < time_threshold:
                    continue
                
                # Extract tweet data
                tweet_info = {
                    'id': tweet.id_str,
                    'text': tweet.full_text,
                    'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'is_retweet': hasattr(tweet, 'retweeted_status'),
                    'is_reply': tweet.in_reply_to_status_id is not None,
                    'url': f"https://twitter.com/elonmusk/status/{tweet.id_str}"
                }
                
                # Add media information if available
                if hasattr(tweet, 'extended_entities') and 'media' in tweet.extended_entities:
                    tweet_info['media'] = [
                        {
                            'type': media['type'],
                            'url': media['media_url_https']
                        }
                        for media in tweet.extended_entities['media']
                    ]
                
                tweets_data.append(tweet_info)
                
                # Break if we have enough tweets
                if len(tweets_data) >= count:
                    break
            
            # Prepare user information
            user_info = {
                'id': user.id_str,
                'name': user.name,
                'screen_name': user.screen_name,
                'description': user.description,
                'followers_count': user.followers_count,
                'friends_count': user.friends_count,
                'statuses_count': user.statuses_count,
                'profile_image_url': user.profile_image_url_https,
                'verified': user.verified
            }
            
            # Prepare final result
            result = {
                'tweets': tweets_data,
                'user_info': user_info,
                'retrieved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'query_params': {
                    'count': count,
                    'include_retweets': include_retweets,
                    'include_replies': include_replies,
                    'hours_back': hours_back
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in MuskTwitterTool: {e}", exc_info=True)
            return f"Error: {e}"