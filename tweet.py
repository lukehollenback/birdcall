import argparse

from birdcall import birdcall

if __name__ == "__main__":
    #
    # Parse arguments.
    #
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--path", help="file or directory (random will be chosen) of file to tweet")
    arg_parser.add_argument("--media", help="file or directory (random will be chosen) of media to attach to tweet")
    arg_parser.add_argument(
        "--delete-content",
        action="store_true",
        help="delete the tweet's content file after posting"
    )
    arg_parser.add_argument("--delete-media", action="store_true", help="delete the tweet's media file after posting")

    args = arg_parser.parse_args()

    #
    # Authenticate and run the logic.
    #
    o = birdcall.Birdcall()
    o.auth()
    o.tweet(args.path, args.media, args.delete_content, args.delete_media)
