import argparse
import time

import tweepy

import auth

"""
Given the id of a tweet, retweets replies to it. Optionally allows for the root reply or a tweet
that it links to to be retweets. Also supports liking the replies and following their authors.
"""
def retweet_replies(
    api: tweepy.API,
    tweet_id,
    like = False,
    follow = False,
    max_retweets = 7,
    delay = 30,
    traverse_quotes = False
):    
    #
    # Fetch a set of muted user ids. We will make sure to not retweet anything by these users (for some
    # reason, muted users' tweets occasionally slip through the search filter).
    #
    muted_ids = [ ]
    
    for mute_id in tweepy.Cursor(api.mutes_ids).items():
        muted_ids.append(mute_id)
    
    print(f"Loaded {len(muted_ids)} mutes.")
    
    #
    # Query for replies to the specified tweet.
    #
    tweet = api.get_status(tweet_id, include_entities = False)
    query = f"to:{tweet.user.screen_name} -from:{tweet.user.screen_name}"
    
    print(f"Searching for \"{query}\".")
    
    count = 0
    
    for result in tweepy.Cursor(api.search, q = query, since_id = tweet.id, include_entities = False).items():
        #
        # Make sure we actually care about this tweet.
        #
        # NOTE: Because we are using the basic Twitter API (rather than the premium or enterprise
        #  versions), there is a chance that our result set will include tweets that were replies to
        #  more recent tweet than the desired one. We must filter out such results manually.
        #
        if result.in_reply_to_status_id != tweet.id:
            print(f"Skipping {result.id} as it is not a reply to {tweet.id}.")
    
            continue
    
        if result.user.id in muted_ids:
            print(f"Skipping tweet ({result.id}) from muted user ({result.user.id}).")
    
            continue
    
        print(f"Processing reply {result.id}.")
    
        #
        # Determine the tweet (either the reply, or a tweet quoted in the reply) that we would actually
        # like to process.
        #
        reply = result
    
        if traverse_quotes and hasattr(result, "quoted_status"):
            # NOTE: The Tweet.quoted_status payload does not contain some useful flags – like favorited
            #  or retweeted. So, unfortunately, we must fetch the full Tweet object for the quote.
    
            reply = api.get_status(result.quoted_status_id, include_entities = False)
    
            print(f"Traversed to quoted tweet ({reply.id}) in reply {result.id}).")
    
        #
        # If we have already retweeted the reply, skip it.
        #
        # NOTE: The "retweeted" and "favorited" flags of the Twitter API's "Tweet" object do not appear
        #  to be bullet-proof. So this is a best-effort check, but we still must handle failures
        #  below.
        #
        if reply.retweeted:
            print(f"Skipping {result.id} as we have already processed it.")
    
            continue
        
        #
        # Retweet, like, and follow the author of the actual tweet that we need to process. If we
        # traversed into quoted tweets and liking is enabled, we also make sure to like the parent
        # tweet.
        #
        # NOTE: Since the core goal of this script is to retweet, a retweet failure will skip all other
        #  desired actions (e.g. liking the tweet or following its author).
        #
        try:
            api.retweet(reply.id)
    
            print("Retweeted %d." % reply.id)
        except tweepy.TweepError as e:
            print(f"Failed to retweet {reply.id}. Will not count it. (error: {e})")
    
            continue
    
        if like:
            try:
                api.create_favorite(reply.id)
    
                print("Liked %d." % reply.id)
            except tweepy.TweepError as e:
                print(f"Failed to like {reply.id}. (error: {e})")
    
            if reply != result:
                try:
                    api.create_favorite(result.id)
    
                    print("Liked %d." % result.id)
                except tweepy.TweepError as e:
                    print(f"Failed to like {result.id}. (error: {e})")
    
        
        if follow:
            try:
                api.create_friendship(reply.user.id)
    
                print("Followed %d." % reply.user.id)
            except tweepy.TweepError as e:
                print(f"Failed to follow {reply.id}'s author ({reply.user.id}). (error: {e})")
    
        #
        # Increment the count and bail if we have retweeted our maximum number of replies.
        #
        count += 1
    
        if count >= max_retweets:
            break
    
        #
        # Wait the delay interval so that we don't spam the Twitter API.
        #
        time.sleep(delay)
    
    #
    # Log how many replies we found and retweeted.
    #
    print(f"Retweeted {count} replies to {tweet.id}.")

if __name__=="__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()
    
    arg_parser.add_argument("--tweet-id", help = "id of tweet to reply the replies of", default = 1412795507118731275)
    arg_parser.add_argument("--like", action = "store_true", help = "like tweets that get retweeted")
    arg_parser.add_argument("--follow", action = "store_true", help = "like authors of tweets that get retweeted")
    arg_parser.add_argument("--max-retweets", default = 7, help = "maximum number of replies to retweet")
    arg_parser.add_argument("--delay", default = 30, help = "seconds betweet retweets")
    arg_parser.add_argument("--traverse-quotes", action = "store_true", help = "retweets quoted tweets instead of parent tweets when they exist")
    
    args = arg_parser.parse_args()
    
    print(f"Arguments = {args}.")

    #
    # Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
    #
    api = auth.authenticate()
    
    #
    # Run logic.
    #
    retweet_replies(
        api,
        args.tweet_id,
        args.like,
        args.follow,
        args.max_retweets,
        args.delay,
        args.traverse_quotes
    )