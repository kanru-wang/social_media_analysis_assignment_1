# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 16:53:19 2018

@author: Kevin
"""

import tweepy
from tweepy import Cursor
from twitterClient import twitterClient
import json
import time

def limit_handled(cursor):
   while True:
      try:
          yield cursor.next()
      except tweepy.RateLimitError:
          time.sleep(5 * 60)

# As of 2018-04-07, if setting  since="2018-03-28", until="2018-04-08", tweets
# from 2018-03-28 07:16:50 to 2018-04-07 08:34:17 is retrieved.
# Tweets earlier than 2018-03-28 cannot be retrieved, even if "since" is set
# earlier. We can conclude this method can retrieve upto 10 day's past tweets.
          
def main():
   client = twitterClient()
   counter = 0
   with open('tweet.json', 'w') as file:
      for tweet in limit_handled(Cursor(client.search,
                                        q="dogecoin",
                                        since="2018-03-28",
                                        until="2018-04-08",
                                        lang ="en", count=100).items()):
         file.write(json.dumps(tweet._json) + "\n")
         counter += 1
         print(counter)

if __name__ == '__main__':
   main()
   
   
   
# This chunk does something different.
#def main():
#   client = twitterClient()

#   with open('tweet.json', 'w') as file:
#      for tweet in Cursor(client.user_timeline, screen_name="@fitbit").items(2000):
#         file.write(json.dumps(tweet._json) + "\n")
