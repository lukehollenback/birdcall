"""
Given the handle of a Twitter user, download all of their followers into a CSV file for further
archiving and/or analysis.
"""

import argparse
import csv
import os.path

import tweepy

import auth

#
# Parse arguments.
#
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--user", help = "handle of the user to download followers of")
arg_parser.add_argument("--output", help = "file to save followers to in CSV format", default = "followers.csv")
arg_parser.add_argument("--append", action = "store_true", help = "only append new followers to output file")

args = arg_parser.parse_args()

print(f"Arguments = {args}.")

#
# Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
#
api = auth.authenticate()

#
# If we are doing an append-only download, load the currently-downloaded followers into memory.
#
rows = []

if args.append and os.path.exists(args.output):
    with open(args.output, mode="r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            #
            # Skip the header row.
            #
            if len(rows) == 0:
                continue

            #
            # Load the line.
            #
            rows.append(row)

        print(f"Loaded {len(rows)} followers.")

#
# Download all of the specified user's followers.
#
for user in tweepy.Cursor(api.followers, include_user_entities = False, screen_name = args.user, count = 200).items():
    #
    # Add the follower to the list of downloaded followers if they are not already in it.
    #
    if not next((row for row in rows if row["id"] == user.id), None):
        row = {
            "id" : user.id,
            "screen_name" : user.screen_name,
            "name" : user.name,
            "location" : user.location,
            "bio" : user.description,
            "website" : user.url,
            "direct_message_link" : (f"https://twitter.com/messages/compose?recipient_id=%d" % user.id),
            "direct_messaged" : False
        }

        rows.append(row)

#
# Output the results.
#
with open(args.output, mode="w") as f:
    writer = csv.DictWriter(f, fieldnames = rows[0].keys())

    writer.writeheader()
    writer.writerows(rows)

#
# Output some debug information.
#
print(f"Downloaded {len(rows)} followers to {args.output}.")