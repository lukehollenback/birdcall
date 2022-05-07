import argparse

from birdcall import birdcall

if __name__ == "__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--query", help="Twitter search query to use to find retweetable tweets")
    arg_parser.add_argument("--friends", action="store_true", help="explicitly add friends to the query filter")
    arg_parser.add_argument("--followers", action="store_true", help="explicitly add followers to the query filter")
    arg_parser.add_argument("--members",
                            help="explicitly add members of the list with the specified id to the query filter")
    arg_parser.add_argument("--filter-count", default=15, help="max number of authorship filters to add to the query")
    arg_parser.add_argument("--like", action="store_true", help="like tweets that get retweeted")
    arg_parser.add_argument("--follow", action="store_true", help="like authors of tweets that get retweeted")

    args = arg_parser.parse_args()

    print(f"Arguments = {args}.")

    #
    # Authenticate and run the logic.
    #
    o = birdcall.Birdcall()
    o.auth()
    o.retweet_search(
        args.query,
        args.friends,
        args.followers,
        args.members,
        args.filter_count,
        args.like,
        args.follow
    )
