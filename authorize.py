"""
Performs an OAuth 1a handshake to authorize a Twitter account to use this app and returns an access
token and secret that this app can use to act on behalf of said authorized user.
"""

import os

import tweepy
from dotenv import load_dotenv

#
# Load environment variables. We specifically need the app's consumer key and secret here.
#
load_dotenv()

TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

#
# Open up a web browser where the Twitter account can be logged into.
#
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)

try:
    redirect_url = auth.get_authorization_url()
except tweepy.TweepError:
    print('Error! Failed to generate access request URL.')

print(f"STEP 1: Go to {redirect_url} and authorize the desired Twitter account.")

verifier_code = input("STEP 2: Enter Twitter authorization PIN: ")

#
# Exchange the verifier code for an access token and secret.
#
try:
    auth.get_access_token(verifier_code)
except tweepy.TweepError:
    print('Error! Failed to get access token and secret.')

print("----------------------")
print(f"        Access Token: {auth.access_token}")
print(f" Access Token Secret: {auth.access_token_secret}")