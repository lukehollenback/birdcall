import argparse

from birdcall import birdcall

if __name__ == "__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--user", help="handle of the user to download followers of")
    arg_parser.add_argument("--output", help="file to save followers to in CSV format", default="followers.csv")
    arg_parser.add_argument("--append", action="store_true", help="only append new followers to output file")

    args = arg_parser.parse_args()

    print(f"Arguments = {args}.")

    #
    # Authenticate and run the logic.
    #
    o = birdcall.Birdcall()
    o.auth()
    o.download_followers(args.user, args.output, args.append)
