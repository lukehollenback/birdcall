import argparse
import csv
import os.path

import tweepy

import auth

"""
Given the handle of a Twitter user, download all of their followers into a CSV file for further
archiving and/or analysis.
"""
def download_followers(user, output, append = False):
    #
    # Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
    #
    api = auth.authenticate()
    
    #
    # If we are doing an append-only download, load the currently-downloaded followers into memory.
    #
    rows = []
    header_read = False
    
    if append and os.path.exists(output):
        with open(output, mode="r") as f:
            reader = csv.DictReader(f)
    
            for row in reader:
                rows.append(row)
    
        print(f"Loaded {len(rows)} followers.")
    
    #
    # Download all of the specified user's followers.
    #
    downloaded_count = 0
    
    for user in tweepy.Cursor(api.followers, include_user_entities = False, screen_name = user, count = 200).items():
        #
        # Add the follower to the list of downloaded followers if they are not already in it.
        #
        # NOTE: We must cast values from the CSV file and values from the the Twitter API to the same
        #  type so that the comparison can work.
        #
        if not next((row for row in rows if int(row["id"]) == int(user.id)), None):
            downloaded_count += 1
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
    
    print(f"Downloaded {downloaded_count} followers.")
    
    #
    # Output the results.
    #
    with open(output, mode="w") as f:
        writer = csv.DictWriter(f, fieldnames = rows[0].keys())
    
        writer.writeheader()
        writer.writerows(rows)
    
    #
    # Output some debug information.
    #
    print(f"Saved {len(rows)} followers to {output}.")

if __name__=="__main__":
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
    # Run logic.
    #
    download_followers(args.user, args.output, args.append)