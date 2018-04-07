"""
COSC2671 Social Media and Network Analytics
@author Jeffrey Chan, 2018

"""

import sys
from argparse import ArgumentParser
import string
import json
import codecs
import re

import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

from colorama import Fore, Back, Style
import pandas as pd
import matplotlib.pyplot as plt

# --posWordFile "positive-words.txt" --negWordFile "negative-words.txt" --tweetsFile "tweet.json" --print --ts --approach "count"
# --posWordFile "positive-words.txt" --negWordFile "negative-words.txt" --tweetsFile "tweet.json" --print --ts --approach "vader"
# https://www.youtube.com/watch?v=cdblJqEUDNo

def buildParser():
    """
    Constructs the command line argument parser.

    @return: parser object
    """

    parser = ArgumentParser()
    # look at the help= part to understand what the argument is for
    parser.add_argument('--posWordFile', help='input file of set of postive words')
    parser.add_argument('--negWordFile', help='input file of set of negative words')
    parser.add_argument('--tweetsFile', help='input file of set of tweets (json format)')
    parser.add_argument('--print', dest='print', action='store_true', help='flag to determine whether to print out tweets and their sentiment')
    parser.add_argument('--ts', dest='ts', action='store_true',
                        help='flag to determine whether to display a time series of the sentiment over time')
    parser.add_argument('--approach', default='count', help='specify the approach to take, one of [count, vader]')

    return parser




def countWordSentimentAnalysis(setPosWords, setNegWords, sTweetsFilename, bPrint, tweetProcessor):
    """
    Basic sentiment analysis.  Count the number of positive words, count the negative words, overall polarity is the
    difference in the two numbers.

    @param setPosWords: set of positive sentiment words
    @param setNegWords: set of negative sentiment words
    @param sTweetsFilename: name of input file containing a json formated tweet dump
    @param bPrint: whether to print the stream of tokens and sentiment.  Uses colorama to highlight sentiment words.
    @param tweetProcessor: TweetProcessing object, used to pre-process each tweet.

    @returns: list of tweets, in the format of [date, sentiment]
    """


    lSentiment = []
    # open file and process tweets, one by one
    with open(sTweetsFilename, 'r') as f:
        for line in f:
            # each line is loaded according to json format, into tweet, which is actually a dictionary
            tweet = json.loads(line)

            try:
                tweetText = tweet.get('text', '')
                tweetDate = tweet.get('created_at')
                # pre-process the tweet text
                lTokens = tweetProcessor.process(tweetText)

                # compute the sentiment (TODO: you are to implement this, go to the function definition)
                sentiment = computeSentiment(lTokens, setPosWords, setNegWords)

                # save the date and sentiment of each tweet (used for time series)
                lSentiment.append([pd.to_datetime(tweetDate), sentiment])

                # if we are printing, each token is printed and coloured according to red if positive word, and blue
                # if negative
                if bPrint:
                    for token in lTokens:
                        if token in setPosWords:
                            print(Fore.RED + token + ', ', end='')
                        elif token in setNegWords:
                            print(Fore.BLUE + token + ', ', end='')
                        else:
                            print(Style.RESET_ALL + token + ', ', end='')

                    print(': {}'.format(sentiment))


            except KeyError as e:
                pass

    return lSentiment



def vaderSentimentAnalysis(sTweetsFilename, bPrint, tweetProcessor):
    """
    Use Vader lexicons instead of a raw positive and negative word count.

    @param sTweetsFilename: name of input file containing a json formated tweet dump
    @param bPrint: whether to print the stream of tokens and sentiment.  Uses colorama to highlight sentiment words.
    @param tweetProcessor: TweetProcessing object, used to pre-process each tweet.

    @returns: list of tweets, in the format of [date, sentiment]
    """

    # this is the vader sentiment analyser, part of nltk
    sentAnalyser = SentimentIntensityAnalyzer()


    lSentiment = []
    # open file and process tweets, one by one
    with open(sTweetsFilename, 'r') as f:
        for line in f:
            # each line is loaded according to json format, into tweet, which is actually a dictionary
            tweet = json.loads(line)

            try:
                tweetText = tweet.get('text', '')
                tweetDate = tweet.get('created_at')
                # pre-process the tweet text
                lTokens = tweetProcessor.process(tweetText)

                # this computes the sentiment scores (called polarity score in nltk, but mean same thing essentially)
                # see lab sheet for what dSentimentScores holds
                dSentimentScores = sentAnalyser.polarity_scores(" ".join(lTokens))

                # save the date and sentiment of each tweet (used for time series)
                lSentiment.append([pd.to_datetime(tweetDate), dSentimentScores['compound']])

                # if we are printing, we print the tokens then the sentiment scores.  Because we don't have the list
                # of positive and negative words, we cannot use colorama to label each token
                if bPrint:
                    print(*lTokens, sep=', ')
                    for cat,score in dSentimentScores.items():
                        print('{0}: {1}, '.format(cat, score), end='')
                    print()

            except KeyError as e:
                pass


    return lSentiment






def computeSentiment(lTokens, setPosWords, setNegWords):
    """
    Compute the sentiment value by subtracting the number of negative words from the number of positive words in the input
    list of tokens.


    @param lTokens:
    @return: sentiment value of the list of tokens
    """

    # TODO: count the number of positive words
    # Answer
    posNum = len([tok for tok in lTokens if tok in setPosWords])
    # TODO: count the number of negative words
    negNum = len([tok for tok in lTokens if tok in setNegWords])


    # TODO: compute the sentiment value
    # replace the right hand side with how to compute the sentiment value
    sentimentVal = posNum - negNum

    return sentimentVal;




class TwitterProcessing:
    """
    This class is used to pre-process tweets.  This centralises the processing to one location.  Feel free to add.
    """

    def __init__(self, tokeniser, lStopwords):
        """
        Initialise the tokeniser and set of stopwords to use.

        @param tokeniser:
        @param lStopwords:
        """

        self.tokeniser = tokeniser
        self.lStopwords = lStopwords



    def process(self, text):
        """
        Perform the processing.
        @param text: the text (tweet) to process

        @returns: list of (valid) tokens in text
        """

        text = text.lower()
        tokens = self.tokeniser.tokenize(text)
        tokensStripped = [tok.strip() for tok in tokens]

        # pattern for digits
        # the list comprehension in return statement essentially remove all strings of digits or fractions, e.g., 6.15
        regexDigit = re.compile("^\d+\s|\s\d+\s|\s\d+$")
        # regex pattern for http
        regexHttp = re.compile("^http")

        return [tok for tok in tokensStripped if tok not in self.lStopwords and regexDigit.match(tok) == None and regexHttp.match(tok) == None]



def main():
    """
    Main function, performs unsupervised sentiment analysis.
    """

    # command line parsing
    parser = buildParser()
    args = parser.parse_args()


    # construct the tweet pro-processing object
    tweetTokenizer = TweetTokenizer()
    lPunct = list(string.punctuation)
    lStopwords = stopwords.words('english') + lPunct + ['rt', 'via', '...', '…', '"', "'", '`']

    tweetProcessor = TwitterProcessing(tweetTokenizer, lStopwords)


    # load set of positive words
    lPosWords = []
    with open(args.posWordFile, 'r', encoding='utf-8', errors='ignore') as fPos:
        for sLine in fPos:
            lPosWords.append(sLine.strip())

    setPosWords = set(lPosWords)


    # load set of negative words
    lNegWords = []
    with codecs.open(args.negWordFile, 'r', encoding='utf-8', errors='ignore') as fNeg:
        for sLine in fNeg:
            lNegWords.append(sLine.strip())

    setNegWords = set(lNegWords)

    # compute the sentiment
    lSentiment = []
    if args.approach == 'count':
        lSentiment = countWordSentimentAnalysis(setPosWords, setNegWords, args.tweetsFile, args.print, tweetProcessor)
    elif args.approach == 'vader':
        lSentiment = vaderSentimentAnalysis(args.tweetsFile, args.print, tweetProcessor)


    # determine if we should output a time series of sentiment scores across time
    if args.ts:
        # TODO: write code to display the time series
        # we are using pandas for this, but first we need to get it into a pandas data frame structure
        series = pd.DataFrame(lSentiment, columns=['date', 'sentiment'])
        # tell pandas that the date column is the one we use for indexing (or x-axis)
        series.set_index('date', inplace=True)
        # pandas makes a guess at the type of the columns, but to make sure it doesn't get it wrong, we set the sentiment
        # column to floats
        series[['sentiment']] = series[['sentiment']].apply(pd.to_numeric)

        # This step is not necessary, but pandas has a neat function that allows us to group the series at different
        # resultion.  The 'how=' part tells it how to group the instances.  In this example, it sames we want to group
        # by day, and add up all the sentiment scores for the same day and create a new time series called 'newSeries'
        # with this day resolution
        # TODO: play with this for different resolution, '1H' is by hour, '1M' is by minute etc
        #newSeries = series.resample('1D', how='sum')
        newSeries = series.resample('1H', how='sum')
        # this plots and shows the time series
        newSeries.plot()
        plt.show()


################################################################




if __name__ == "__main__":
    main()