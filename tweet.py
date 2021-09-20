"""
Tweets the content of a file, or of a random file in a directory.
"""

import argparse
import os
import random

import auth

#
# Parse arguments.
#
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--path", help = "file or directory (random will be chosen) of file to tweet")
arg_parser.add_argument("--media", help = "file or directory (random will be chosen) of media to attach to tweet")
arg_parser.add_argument("--delete-content", action = "store_true", help = "delete the tweet's content file after posting")
arg_parser.add_argument("--delete-media", action = "store_true", help = "delete the tweet's media file after posting")

args = arg_parser.parse_args()

print(f"Arguments = {args}.")

#
# Seed the random number generator so that we don't get the same results every time the script runs.
#
random.seed()

#
# Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
#
api = auth.authenticate()

#
# Determine whether we are dealing with a single file or a directory of files containing content to
# tweet.
#
is_directory = os.path.isdir(args.path)

if is_directory:
    args.path = f"{args.path}/{random.choice(os.listdir(args.path))}"

#
# If a media attachment was specified, determine whether we are dealing with a single file or a
# directory of files containing the media to upload.
#
if args.media:
    is_directory = os.path.isdir(args.media)

    if is_directory:
        args.media = f"{args.media}/{random.choice(os.listdir(args.media))}"

#
# Load the content that will be tweeted.
#
with open(args.path, "r") as file:
    content = file.read()

    #
    # Tweet the content.
    #
    if args.media:
        tweet = api.update_with_media(args.media, content)
    else:
        tweet = api.update_status(content)

    #
    # Print out the id of the new tweet (in case it needs to be piped into another script).
    #
    print(tweet.id)

#
# Delete files if necessary.
#
if args.delete_content:
    os.remove(args.path)
    
if args.media and args.delete_media:
    os.remove(args.media)