import argparse

from birdcall import birdcall

if __name__ == "__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--tweet-id", help="id of tweet to reply the replies of", default=1412795507118731275)
    arg_parser.add_argument("--like", action="store_true", help="like tweets that get retweeted")
    arg_parser.add_argument("--follow", action="store_true", help="like authors of tweets that get retweeted")
    arg_parser.add_argument("--max-retweets", default=7, help="maximum number of replies to retweet")
    arg_parser.add_argument("--delay", default=30, help="seconds retweet retweets")
    arg_parser.add_argument("--traverse-quotes", action="store_true",
                            help="retweets quoted tweets instead of parent tweets when they exist")

    args = arg_parser.parse_args()

    print(f"Arguments = {args}.")

    #
    # Authenticate and run the logic.
    #
    o = birdcall.Birdcall()
    o.auth()
    o.retweet_replies(
        args.tweet_id,
        args.like,
        args.follow,
        args.max_retweets,
        args.delay,
        args.traverse_quotes
    )
