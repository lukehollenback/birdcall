"""
Unfollows anyone that is not currently following the authenticated user.
"""

import tweepy

import auth

#
# Authenticate w/Twitter and obtain a Tweepy API handle that can be used for requests.
#
api = auth.authenticate()
me = api.me()

#
# Iterate through all friends. Destroy the friendship if they are not following us.
#
count = 0

for friend in tweepy.Cursor(api.friends, skip_status = True, include_user_entities = False).items():
    relationship = api.show_friendship(source_id = me.id, target_id = friend.id)
    
    if not relationship[0].followed_by:
        api.destroy_friendship(friend.id)

        count += 1

        print(f"Unfollowed {friend.id} ({friend.screen_name}).")

print(f"Unfollowed {count} users.")