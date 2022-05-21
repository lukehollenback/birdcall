import array
import csv
from datetime import date
import os.path
import random
import time

from dotenv import load_dotenv
import tweepy


class Birdcall:
    api: tweepy.API = None

    def auth(self, consumer_key=None, consumer_secret=None, access_token=None, access_secret=None):
        """
        Authenticates with the Twitter API using the consumer key, consumer secret, access token, and
        access secret set in the runtime environment. Returns an authenticated API client that can be used
        to make calls.
        """

        #
        # Load environment variables.
        #
        load_dotenv()

        twitter_consumer_key = os.getenv('TWITTER_CONSUMER_KEY', consumer_key)
        twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET', consumer_secret)
        twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN', access_token)
        twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET', access_secret)

        #
        # Authenticate w/Twitter and store the authenticated client.
        #
        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
        auth.set_access_token(twitter_access_token, twitter_access_secret)

        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def download_followers(self, user: str, output: str, append: bool = False):
        """
        Given the handle of a Twitter user, download all of their followers into a CSV file for further
        archiving and/or analysis.
        """

        #
        # If we are doing an append-only download, load the currently-downloaded followers into memory.
        #
        rows = []

        if append and os.path.exists(output):
            with open(output, mode="r") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    rows.append(row)

            print(f"Loaded {len(rows)} followers.")

        #
        # Download all the specified user's followers.
        #
        downloaded_count = 0

        for user in tweepy.Cursor(
                self.api.get_followers,
                count=1000,
                include_user_entities=False,
                screen_name=user
        ).items():
            #
            # Add the follower to the list of downloaded followers if they are not already in it.
            #
            # NOTE: We must cast values from the CSV file and values from the Twitter API to the same
            #  type so that the comparison can work.
            #
            if not next((row for row in rows if int(row["id"]) == int(user.id)), None):
                downloaded_count += 1
                row = {
                    "id": user.id,
                    "screen_name": user.screen_name,
                    "name": user.name,
                    "location": user.location,
                    "bio": user.description,
                    "website": user.url,
                    "direct_message_link": (f"https://twitter.com/messages/compose?recipient_id=%d" % user.id),
                    "direct_messaged": False
                }

                rows.append(row)

        print(f"Downloaded {downloaded_count} followers.")

        #
        # Output the results.
        #
        with open(output, mode="w") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())

            writer.writeheader()
            writer.writerows(rows)

        #
        # Output some debug information.
        #
        print(f"Saved {len(rows)} followers to {output}.")

    def retweet_replies(
            self,
            tweet_query=None,
            tweet_query_count=3,
            tweet_id=None,
            like=False,
            follow=False,
            max_retweets=7,
            delay=30,
            traverse_quotes=False
    ):
        """
        Given the id of a tweet, retweets replies to it. Optionally allows for the root reply or a tweet
        that it links to be retweets. Also supports liking the replies and following their authors.
        """

        #
        # Fetch a set of muted user ids. We will make sure to not retweet anything by these users (for some
        # reason, muted users' tweets occasionally slip through the search filter).
        #
        muted_ids = []

        for mute_id in tweepy.Cursor(self.api.get_muted_ids).items():
            muted_ids.append(mute_id)

        print(f"Loaded {len(muted_ids)} mutes.")

        #
        # Query for replies to the specified tweet.
        #
        # NOTE: This is a bit of a tricky section. We first try to find the tweets that we care about replies to. Then,
        #  since we cannot directly query for replies to a specific Tweet using Twitter's standard API, we have to
        #  simply query for all recent replies to the authors of the desired tweets and do manual filtering.
        #

        # Build up a chronologically-ordered list of ids and authors of the tweets that we want to find replies to.
        tweet_ids = []
        tweet_authors = []

        if tweet_id is not None:
            tweet = self.api.get_status(tweet_id, include_entities=False)
            tweet_ids.append(tweet.id)
            tweet_authors.append(tweet.user.screen_name)

        if tweet_query is not None:
            for tweet in tweepy.Cursor(
                    self.api.search_tweets,
                    q=tweet_query,
                    count=tweet_query_count,
                    include_entities=False
            ).items():
                if tweet.id not in tweet_ids:
                    tweet_ids.append(tweet.id)

                if tweet.user.screen_name not in tweet_authors:
                    tweet_authors.append(tweet.user.screen_name)

        tweet_ids = sorted(tweet_ids)

        # Build up and execute the query.
        query = ""

        for tweet_author in tweet_authors:
            if len(query) > 0:
                query += " OR "

            query += f"(to:{tweet_author} -from:{tweet_author})"

        print(f"Searching for \"{query}\".")

        count = 0

        for result in tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                since_id=tweet_ids[0],
                include_entities=False
        ).items():
            #
            # Make sure we actually care about this tweet.
            #
            # NOTE: Because we are using the basic Twitter API (rather than the premium or enterprise
            #  versions), there is a chance that our result set will include tweets that were replies to
            #  more recent tweet than the desired one. We must filter out such results manually.
            #
            if result.in_reply_to_status_id not in tweet_ids:
                print(f"Skipping {result.id} as it is not a reply to {tweet_ids}.")

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

                reply = self.api.get_status(result.quoted_status_id, include_entities=False)

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
                self.api.retweet(reply.id)

                print("Retweeted %d." % reply.id)
            except tweepy.TweepyException as e:
                print(f"Failed to retweet {reply.id}. Will not count it. (error: {e})")

                continue

            if like:
                try:
                    self.api.create_favorite(reply.id)

                    print("Liked %d." % reply.id)
                except tweepy.TweepyException as e:
                    print(f"Failed to like {reply.id}. (error: {e})")

                if reply != result:
                    try:
                        self.api.create_favorite(result.id)

                        print("Liked %d." % result.id)
                    except tweepy.TweepyException as e:
                        print(f"Failed to like {result.id}. (error: {e})")

            if follow:
                try:
                    self.api.create_friendship(reply.user.id)

                    print("Followed %d." % reply.user.id)
                except tweepy.TweepyException as e:
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

    def retweet_search(
            self,
            query,
            friends=False,
            followers=False,
            members=[],
            filter_count=15,
            like=False,
            follow=False
    ):
        """
        Given a search criteria, retweets a random result tweet. Also supports liking of said tweet and
        following its author.
        """

        #
        # Seed the random number generator so that we don't get the same results every time the script runs.
        #
        random.seed()

        #
        # Fetch a set of muted user ids. We will make sure to not retweet anything by these users (for some
        # reason, muted users' tweets occasionally slip through the search filter).
        #
        muted_ids = []

        for mute_id in tweepy.Cursor(self.api.get_muted_ids).items():
            muted_ids.append(mute_id)

        print(f"Loaded {len(muted_ids)} mutes.")

        #
        # Interpolate dynamic values into the query.
        #
        query = query.format(today=date.today().strftime("%Y-%m-%d"))

        #
        # Process dynamic authorship filters into the query.
        #
        usernames = []

        if friends:
            for account in tweepy.Cursor(self.api.get_friends, count=1000, skip_status=True, include_user_entities=False).items():
                if account.screen_name not in usernames:
                    usernames.append(account.screen_name)

        if followers:
            for account in tweepy.Cursor(self.api.get_followers, count=1000, skip_status=True, include_user_entities=False).items():
                if account.screen_name not in usernames:
                    usernames.append(account.screen_name)

        if members and len(members) > 0:
            for account in tweepy.Cursor(self.api.get_list_members, list_id=members, count=1000).items():
                if account.screen_name not in usernames:
                    usernames.append(account.screen_name)

        if len(usernames) > 0:
            random.shuffle(usernames)

            count = 0
            query += " ("

            for username in usernames:
                if count > 0:
                    query += " OR "

                query += f"from:{username}"
                count += 1

                if count >= filter_count:
                    break

            query += ")"

        #
        # Perform the search.
        #
        print(f"Searching for \"{query}\".")

        results = self.api.search_tweets(
            q=query,
            result_type='recent',
            include_entities=False,
            count=25
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
            for _ in range(5):
                tweet = random.choice(results)

                if tweet.user.id in muted_ids:
                    print(f"Skipping tweet ({tweet.id}) from muted user ({tweet.user.id}).")

                    continue

                try:
                    self.api.retweet(tweet.id)

                    print("Retweeted %d." % tweet.id)
                except tweepy.TweepyException as e:
                    print(f"Failed to retweet {tweet.id}. (error: {e}")

                    continue

                if like:
                    try:
                        self.api.create_favorite(tweet.id)

                        print("Liked %d." % tweet.id)
                    except tweepy.TweepyException as e:
                        print(f"Failed to like {tweet.id}. (error: {e}")

                if follow:
                    try:
                        self.api.create_friendship(tweet.user.id)

                        print("Followed %d." % tweet.user.id)
                    except tweepy.TweepyException as e:
                        print(f"Failed to follow {tweet.id}'s author ({tweet.user.id}). (error: {e}")

                break

    def tweet(self, tweet_path, media_path=None, delete_content=False, delete_media=False):
        """
        Tweets the content of a file, or of a random file in a directory. The id of the tweet is output and returned so
        that it can be piped into subsequent programs if desired.
        """

        #
        # Seed the random number generator so that we don't get the same results every time the script runs.
        #
        random.seed()

        #
        # Determine whether we are dealing with a single file or a directory of files containing content to
        # tweet.
        #
        is_directory = os.path.isdir(tweet_path)

        if is_directory:
            tweet_path = f"{tweet_path}/{random.choice(os.listdir(tweet_path))}"

        #
        # If a media attachment was specified, determine whether we are dealing with a single file or a
        # directory of files containing the media to upload.
        #
        if media_path:
            is_directory = os.path.isdir(media_path)

            if is_directory:
                media_path = f"{media_path}/{random.choice(os.listdir(media_path))}"

        #
        # Load the content that will be tweeted.
        #
        with open(tweet_path, "r") as file:
            content = file.read()

            #
            # Tweet the content.
            #
            if media_path:
                media = self.api.media_upload(filename=media_path)
                tweet = self.api.update_status(status=content, media_ids=[media.media_id])
            else:
                tweet = self.api.update_status(status=content)

            #
            # Print out the id of the new tweet (in case it needs to be piped into another script).
            #
            print(tweet.id)

        #
        # Delete files if necessary.
        #
        if delete_content:
            os.remove(tweet_path)

        if media_path and delete_media:
            os.remove(media_path)

        #
        # Return the tweet id.
        #
        return tweet.id

    def unfollow_traitors(self):
        """
        Unfollows anyone that is not currently following the authenticated user.
        """

        #
        # Get a handle on the authenticated user.
        #
        me = self.api.verify_credentials()

        #
        # Iterate through all friends. Destroy the friendship if they are not following us.
        #
        count = 0

        for friend in tweepy.Cursor(self.api.get_friends, count=1000, skip_status=True, include_user_entities=False).items():
            relationship = self.api.get_friendship(source_id=me.id, target_id=friend.id)

            if not relationship[0].followed_by:
                try:
                    self.api.destroy_friendship(friend.id)

                    count += 1

                    print(f"Unfollowed {friend.id} ({friend.screen_name}).")
                except tweepy.TweepyException as e:
                    print(f"Failed to unfollow {friend.id} ({friend.screen_name}). (error: {e})")

        print(f"Unfollowed {count} users.")