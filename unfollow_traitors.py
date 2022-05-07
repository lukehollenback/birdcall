import argparse

from birdcall import birdcall

if __name__ == "__main__":
    #
    # Authenticate and run the logic.
    #
    o = birdcall.Birdcall()
    o.auth()
    o.unfollow_traitors()
