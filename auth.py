import os

import tweepy
from dotenv import load_dotenv

#
# Authenticates with the Twitter API using the consumer key, consumer secret, access token, and
# access secret set in the runtime environment. Returns an authenticated API client that can be used
# to make calls.
#
def authenticate() -> tweepy.API:
    #
    # Load environment variables.
    #
    load_dotenv()

    TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

    #
    # Authenticate w/Twitter.
    #
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    return tweepy.API(auth)