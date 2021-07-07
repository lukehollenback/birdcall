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
arg_parser.add_argument("--filters", default = 15, help = "max number of authorship filters to add to the query")
arg_parser.add_argument("--like", action = "store_true", help = "like tweets that get retweeted")
arg_parser.add_argument("--follow", action = "store_true", help = "like authors of tweets that get retweeted")

args = arg_parser.parse_args()

print("Arguments = %s." % args)

#
# Seed the random number generator so that we don't get the same results every time the script runs.
#
random.seed()

#
# Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
#
api = auth.authenticate()

#
# Interpolate dynamic values into the query.
#
query = args.query.format(today = date.today().strftime("%Y-%m-%d"))

#
# Process dynamic authorship filters into the query.
#
# TODO: Eventually, when the bot a lot many followers and friends, this will be too simple. We will
#  have to randomly pick a subset of the relevant users.
#
usernames = [ ]

if args.friends:
    for account in tweepy.Cursor(api.friends, skip_status = True).items():
        if account.screen_name not in usernames:
            usernames.append(account.screen_name)

if args.followers:
    for account in tweepy.Cursor(api.followers, skip_status = True).items():
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

        query += ("from:%s" % username)
        count += 1

        if count >= args.filters:
            break
    
    query += ")"

#
# Perform a search.
#
print("Searching for \"%s\"." % query)

search_results = api.search(
    q = query,
    result_type = 'recent',
    include_entities = False,
    count = 25
)

print("Found %d search results." % len(search_results))

#
# Retweet a random tweet from the search results. Attempt up to five times to find one that the bot
# has not already retweeted.
#
if len(search_results) > 0:
    for i in range(5):
        tweet = random.choice(search_results)

        try:
            if args.like:
                api.create_favorite(tweet.id)

                print("Linked %d." % tweet.id)

            if args.follow:
                api.create_friendship(tweet.user.id)

                print("Followed %d." % tweet.user.id)
            
            api.retweet(tweet.id)

            print("Retweeted %d." % tweet.id)

            break
        except tweepy.TweepError as e:
            print("Failed to retweet. Failure = %s." % e.response.text)
