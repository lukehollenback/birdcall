import tweepy

import auth

class Birdcall:
    
    api: tweepy.API = None
    
    def __init__(self, api: tweepy.API):
        self.api = api

    @staticmethod
    def create() -> Birdcall:
        #
        # Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
        #
        api = auth.authenticate()

        #
        # Build a new Birdcall instance with the obtained API client handle and return it.
        #
        return Birdcall(api)
    
    def download_followers(self, user: str, output: str, append: bool = False):
        download_followers(self.api, user, output, append)
        
    