"""
Given a search criteria, retweets a random result tweet. Also supports liking of said tweet and
following its author.
"""

import random
import argparse
from datetime import date

import tweepy

import auth

#
# Parse arguments.
#
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--query", help = "Twitter search query to use to find retweetable tweets")
arg_parser.add_argument("--friends", action = "store_true", help = "explicitly add friends to the query filter")
arg_parser.add_argument("--followers", action = "store_true", help = "explicitly add followers to the query filter")
arg_parser.add_argument("--members", help = "explicitly add members of the list with the specified id to the query filter")
arg_parser.add_argument("--filter-count", default = 15, help = "max number of authorship filters to add to the query")
arg_parser.add_argument("--like", action = "store_true", help = "like tweets that get retweeted")
arg_parser.add_argument("--follow", action = "store_true", help = "like authors of tweets that get retweeted")

args = arg_parser.parse_args()

print(f"Arguments ={args}.")

#
# Seed the random number generator so that we don't get the same results every time the script runs.
#
random.seed()

#
# Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
#
api = auth.authenticate()

#
# Fetch a set of muted user ids. We will make sure to not retweet anything by these users (for some
# reason, muted users' tweets occasionally slip through the search filter).
#
muted_ids = [ ]

for mute_id in tweepy.Cursor(api.mutes_ids).items():
    muted_ids.append(mute_id)

print(f"Loaded {len(muted_ids)} mutes.")

#
# Interpolate dynamic values into the query.
#
query = args.query.format(today = date.today().strftime("%Y-%m-%d"))

#
# Process dynamic authorship filters into the query.
#
usernames = [ ]

if args.friends:
    for account in tweepy.Cursor(api.friends, skip_status = True, include_user_entities = False).items():
        if account.screen_name not in usernames:
            usernames.append(account.screen_name)

if args.followers:
    for account in tweepy.Cursor(api.followers, skip_status = True, include_user_entities = False).items():
        if account.screen_name not in usernames:
            usernames.append(account.screen_name)

if args.members and len(args.members) > 0:
    for account in tweepy.Cursor(api.list_members, list_id = args.members).items():
        if account.screen_name not in usernames:
            usernames.append(account.screen_name)

if len(usernames) > 0:
    random.shuffle(usernames)

    count = 0
    query += " ("

    for username in usernames:
        if count > 0:
            query += " OR "

        query += (f"from:{username}")
        count += 1

        if count >= args.filter_count:
            break
    
    query += ")"

#
# Perform the search.
#
print(f"Searching for \"{query}\".")

results = api.search(
    q = query,
    result_type = 'recent',
    include_entities = False,
    count = 25
)

print(f"Found {len(results)} search results.")

#
# Retweet a random tweet from the search results. Attempt up to five times to find one that the bot
# has not already retweeted.
#
# NOTE: Since the goal of this script is primarily to retweet, we try to do that first. If it fails,
#  we burn the attempt and move on to another. Otherwise, we proceed to try to like the tweet and
#  follow its author.
#
if len(results) > 0:
    for i in range(5):
        tweet = random.choice(results)

        if tweet.user.id in muted_ids:
            print(f"Skipping tweet ({tweet.id}) from muted user ({tweet.user.id}).")

            continue

        try:
            api.retweet(tweet.id)

            print("Retweeted %d." % tweet.id)
        except tweepy.TweepError as e:
            print(f"Failed to retweet {tweet.id}. (error: {e.response.text}")

            continue

        if args.like:
            try:
                api.create_favorite(tweet.id)

                print("Liked %d." % tweet.id)
            except tweepy.TweepError as e:
                print(f"Failed to like {tweet.id}. (error: {e.response.text}")

        if args.follow:
            try:
                api.create_friendship(tweet.user.id)

                print("Followed %d." % tweet.user.id)
            except tweepy.TweepError as e:
                print(f"Failed to follow {tweet.id}'s author ({tweet.user.id}). (error: {e.response.text}")

        break
