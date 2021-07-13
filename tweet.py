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

arg_parser.add_argument("--path", help = "file or directory (random will be chosen) of files to tweet")

args = arg_parser.parse_args()

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
# Load the content that will be tweeted.
#
with open(args.path, "r") as file:
    content = file.read()

    #
    # Tweet the content.
    #
    tweet = api.update_status(content)

    #
    # Print out the id of the new tweet (in case it needs to be piped into another script).
    #
    print(tweet.id)