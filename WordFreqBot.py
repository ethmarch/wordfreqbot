##############################################################################
# Word Frequency Twitter Bot                                                 #
# Ethan March                                                                #
#                                                                            #
#                                                                            #
# This is the twitter bot behind the account @WordFreqBot.  Users can tweet  #
# a word at the account and it will tweet back at them telling them the      #
# frequency with which their last 1000 tweets contain that word.             #
##############################################################################

import tweepy
from keys import *
import os
import redis
from math import ceil
########################### Authentication Keys ###############################

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TOKEN_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

############################### Functions #####################################

# gets the searchable word from the tweet
def getword(status):
    text = status.text
    word = text.replace("@WordFreqBot ", "")
    lower = word.lower()
    return lower

# Get user's screen name from tweet
def getuser(status):
    user = status.user.screen_name
    return user

# Counts number of tweets that contain the search word and
# and divides that by the number of tweets.
def wordfreq(tweets, word):
    count = 0
    for status in tweets:
        txt = status.text
        ltext = txt.lower()
        if word in ltext:
            count += 1
        else: count = count
    freq = (count - 1) / 1000
    return freq

#################################################################################
r = redis.from_url(os.environ.get("REDIS_URL"))

id_query = r.get("lastid")
last_id = int(id_query)
id = last_id 

twts = api.search(q="@WordFreqBot", since_id=last_id)

for twt in twts:
    word = getword(twt)
    user = getuser(twt)
    tl = tweepy.Cursor(api.user_timeline, screen_name="%s" % user, count=200).items(1000)
    freq = wordfreq(tl, word)
    str1 = '@%s The word(s) "%s" appear(s) in '  % (user, word)
    str2 = str(ceil(freq * 100)) + '% of the last 1000 tweets on your timeline.'
    response = str1 + str2
    api.update_status(status=response)
if len(twts) > 0:
    first = twts[0]
    id = str(first.id)
else:
    quit()

r.set("lastid", id)

