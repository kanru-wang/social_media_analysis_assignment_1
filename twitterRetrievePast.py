# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 16:53:19 2018

@author: Kevin
"""

from tweepy import Cursor
from twitterClient import twitterClient
import json


def main():
   client = twitterClient()
   #counter = 0
   with open('tweet.json', 'w') as file:
      for tweet in Cursor(client.search, q="dogecoin", #since="2018-03-29",
                          # Do not specify "until" since it will retrieve
                          # until today and specifying "until" will cause
                          # some unknown problem.
                          lang = "en").items(2000):
         file.write(json.dumps(tweet._json) + "\n")
         #counter = counter + 1
         #print(counter)

if __name__ == '__main__':
   main()
   
   
   
# This chunk does something different.
#def main():
#   client = twitterClient()

#   with open('tweet.json', 'w') as file:
#      for tweet in Cursor(client.user_timeline, screen_name="@fitbit").items(2000):
#         file.write(json.dumps(tweet._json) + "\n")
