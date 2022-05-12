from birdcall import Birdcall

birdcall = Birdcall()
birdcall.auth()
birdcall.retweet_search(
    query="((#gamedev #indiedev) OR (#indiedev #indiegame) OR (#indiedev #screenshotsaturday) OR (#indiedev #wishlistwednesday) OR #pico8 OR #tweetcart) since:{today} filter:media filter:safe -filter:retweets",
    like=True
)