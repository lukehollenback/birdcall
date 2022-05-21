from birdcall import Birdcall

birdcall = Birdcall()
birdcall.auth()
birdcall.retweet_search(
    query="((#gamedev #indiedev) OR (#indiedev #indiegame) OR (#indiedev #screenshotsaturday) OR (#indiedev #wishlistwednesday) OR #pico8 OR #tweetcart) since:{today} filter:media filter:safe -filter:retweets",
    like=True
)
birdcall.retweet_replies(tweet_query="from:indiedevtracker #retweet", like=True, traverse_quotes=True)
