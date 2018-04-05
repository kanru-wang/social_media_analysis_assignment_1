#
# COSC2671 Social Media and Network Analytics
# @author Jeffrey Chan, 2018
#

import sys
from collections import Counter
import json


def main():
    # load json file
    # note usually we would do some checks, but for clarify's sake we haven't implement that code here
    fJsonName = sys.argv[1]

    # number of tweets to display
    tweetThres = 50

    # open file and use Counter to count the number of times the hash tags appears
    with open(fJsonName, 'r') as f:
        hashtagsCounter = Counter()
        # for each line in file (which corresponds to a tweet), load it, get the hashtags and insert them into the
        # Counter
        for line in f:
            # Me: this "if" clause is added to skip blank lines between tweets.
            if line not in ['\n', '\r\n']:
                tweet = json.loads(line)
                hashtagsInTweet = getHashtags(tweet)
                hashtagsCounter.update(hashtagsInTweet)

        for tag, count in hashtagsCounter.most_common(tweetThres):
            print(tag + ": " + str(count))


def getHashtags(tweet):
    """
    Extracts the associated hashtags of tweet.

    @param tweet: The tweet, which is in the tweepy json format, and which we wish to extract its associated hashtags.

    @returns: list of hashtags (in lower case)
    """
    entities = tweet.get('entities', {})
    hashtags = entities.get('hashtags', [])

    return [tag['text'].lower() for tag in hashtags]



if __name__ == '__main__':
    main()