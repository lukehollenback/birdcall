import tweepy

import auth

"""
Unfollows anyone that is not currently following the authenticated user.
"""
def unfollow_traitors(api: tweepy.API):
    #
    # Get a handle on the authenticated user.
    #
    me = api.me()

    #
    # Iterate through all friends. Destroy the friendship if they are not following us.
    #
    count = 0

    for friend in tweepy.Cursor(api.friends, skip_status = True, include_user_entities = False).items():
        relationship = api.show_friendship(source_id = me.id, target_id = friend.id)
        
        if not relationship[0].followed_by:
            try:
                api.destroy_friendship(friend.id)

                count += 1

                print(f"Unfollowed {friend.id} ({friend.screen_name}).")
            except tweepy.TweepError as e:
                print(f"Failed to unfollow {friend.id} ({friend.screen_name}). (error: {e})")

            

    print(f"Unfollowed {count} users.")

if __name__=="__main__":
    #
    # Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
    #
    api = auth.authenticate()

    #
    # Run logic.
    #
    unfollow_traitors()