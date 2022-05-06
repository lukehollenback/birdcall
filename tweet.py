import argparse
from asyncio.windows_events import NULL
import os
import random

import tweepy

import auth

"""
Tweets the content of a file, or of a random file in a directory. The id of the the tweet is output
so that it can be piped into subsequent programs if desired.s
"""
def tweet(api: tweepy.API, path, media = NULL, delete_content = False, delete_media = False):
    #
    # Seed the random number generator so that we don't get the same results every time the script runs.
    #
    random.seed()

    #
    # Determine whether we are dealing with a single file or a directory of files containing content to
    # tweet.
    #
    is_directory = os.path.isdir(path)

    if is_directory:
        path = f"{path}/{random.choice(os.listdir(path))}"

    #
    # If a media attachment was specified, determine whether we are dealing with a single file or a
    # directory of files containing the media to upload.
    #
    if media:
        is_directory = os.path.isdir(media)

        if is_directory:
            media = f"{media}/{random.choice(os.listdir(media))}"

    #
    # Load the content that will be tweeted.
    #
    with open(path, "r") as file:
        content = file.read()

        #
        # Tweet the content.
        #
        if media:
            tweet = api.update_with_media(media, content)
        else:
            tweet = api.update_status(content)

        #
        # Print out the id of the new tweet (in case it needs to be piped into another script).
        #
        print(tweet.id)

    #
    # Delete files if necessary.
    #
    if delete_content:
        os.remove(path)
        
    if media and delete_media:
        os.remove(media)

if __name__=="__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--path", help = "file or directory (random will be chosen) of file to tweet")
    arg_parser.add_argument("--media", help = "file or directory (random will be chosen) of media to attach to tweet")
    arg_parser.add_argument("--delete-content", action = "store_true", help = "delete the tweet's content file after posting")
    arg_parser.add_argument("--delete-media", action = "store_true", help = "delete the tweet's media file after posting")

    args = arg_parser.parse_args()

    #
    # Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
    #
    api = auth.authenticate()

    #
    # Run logic.
    #
    tweet(api, args.path, args.media, args.delete_content, args.delete_media)