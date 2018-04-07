"""
COSC2671 Social Media and Network Analytics
@author Jeffrey Chan, 2018

"""

from tweepy import Cursor
from twitterClient import twitterClient
from argparse import ArgumentParser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis.sklearn
from wordcloud import WordCloud

import string
import json
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import numpy as np
import matplotlib.pyplot as plt
import math



# --tweetFile "tweet.json" --resultsToRetrieve 10000


#######################


def main():
    """
    Performs topic modelling on a twitter timeline, and uses pyLDAvis and word clouds to visualise the topics.

    """

    # command line parsing
    parser = buildParser()
    args = parser.parse_args()


    tweetTokenizer = TweetTokenizer()
    punct = list(string.punctuation)
    stopwordList = stopwords.words('english') + punct + ['rt', 'via', '...', '"', "'", '“', '’', '…', '”']


    lTweets = []


    client = twitterClient()


    # Me: commented out the following block, since tweet data is already on-disk.
    
    # own timeline
    #if args.user == None:
    #    for tweet in Cursor(client.home_timeline).items(args.resultsToRetrieve):
    #        lTokens = process(text=tweet.text, tokeniser=tweetTokenizer, stopwords=stopwordList)
    #        lTweets.append(' '.join(lTokens))
    # else retrieve timeline of specified user (available in args.user)
    #else:
    #    for tweet in Cursor(client.user_timeline, screen_name=args.user).items(args.resultsToRetrieve):
    #        lTokens = process(text=tweet.text, tokeniser=tweetTokenizer, stopwords=stopwordList)
    #        lTweets.append(' '.join(lTokens))
    with open(args.tweetFile, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            tweetText = tweet.get('text', '')     # dict.get(key[, default])
            lTokens = process(text=tweetText, tokeniser=tweetTokenizer, stopwords=stopwordList)
            lTweets.append(' '.join(lTokens))
            
    no_features = 1500

    # Me: I am hacking here to plug in a few words into the stopword list of CountVectorizer.
    #     This is the better place to add in more stopwords, instead of doing that at above.
    built_in_stop_words= list(CountVectorizer(stop_words='english').get_stop_words())
    built_in_stop_words = built_in_stop_words + ['dogecoin', 'dogecoins', 'doge', 'https', 'coin', 'coins', 'bitcoin', 'litecoin']
    
    #tfVectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tfVectorizer = CountVectorizer(max_df=0.95, 
                                   min_df=2, 
                                   max_features=no_features, 
                                   stop_words=built_in_stop_words)
    tf = tfVectorizer.fit_transform(lTweets)
    # extract the names of the features (in our case, the words)
    tfFeatureNames = tfVectorizer.get_feature_names()


    # Run LDA
    ldaModel = LatentDirichletAllocation(n_components=args.topicNum, max_iter=10, learning_method='online').fit(tf)

    # print out topics
    display_topics(ldaModel, tfFeatureNames, args.wordNumToDisplay)

    #
    # Word Cloud
    #

    # display wordcloud
    # TODO: go to the function definition and complete its implementation
    displayWordcloud(ldaModel, tfFeatureNames)


    # TODO: Add the pyLDAvis code here
    # note if you also implemented the word cloud, that will display first, then once you close that
    # file, then this will display
    #
    # Answer: pyLDAvis visualisation
    #
    
    # Me: The problem is that spyder has problem display this visulisation in a
    #     browswer window. Therefore this function is commented out.
    #panel = pyLDAvis.sklearn.prepare(ldaModel, tf, tfVectorizer, mds='tsne')
    #pyLDAvis.show(panel)



#######################



def buildParser():
    """
    Constructs the command line argument parser.

    @return: parser object
    """

    parser = ArgumentParser(description='Performs topic modelling and two types of visualisation.')
    # look at the help= part to understand what the argument is for
    parser.add_argument('--topicNum', type=int, default=10, help='number of topics to discover')
    #parser.add_argument('--user', help="Instead of own timeline, will retrieve the specified user's timeline")
    # Me: commented out the previous line, since tweet data is already on-disk.
    parser.add_argument('--tweetFile', help='input file of set of tweets (json format)')
    parser.add_argument('--resultsToRetrieve', help="The number of tweets to retrieve and print.  Default is 500",
                        default=500, type=int)
    # Answer: to control maximum number of words to print
    parser.add_argument('--wordNumToDisplay', type=int, default=10, help='maximum number of words to display per topic')


    return parser



def process(text, tokeniser=TweetTokenizer(), stopwords=[]):
    """
    Perform the processing.

    @param text: the text (tweet) to process
    @param tokeniser: tokeniser to use.
    @param stopwords: list of stopwords to use.

    @returns: list of (valid) tokens in text
    """

    text = text.lower()
    tokens = tokeniser.tokenize(text)
    return [tok for tok in tokens if tok not in stopwords and not tok.isdigit()]


def display_topics(model, featureNames, numTopWords):
    """
    Prints out the most associated words for each feature.

    @param model: lda model.
    @param featureNames: list of strings, representing the list of features/words.
    @param numTopWords: number of words to print per topic.
    """

    # print out the topic distributions
    for topicId, lTopicDist in enumerate(model.components_):
        print("Topic %d:" % (topicId))
        print(" ".join([featureNames[i] for i in lTopicDist.argsort()[:-numTopWords - 1:-1]]))


def displayWordcloud(model, featureNames):
    """
    Displays the word cloud of the topic distributions, stored in model.

    @param model: lda model.
    @param featureNames: list of strings, representing the list of features/words.
    """




    # this normalises each row/topic to sum to one
    # use this normalisedComponents to display your wordclouds
    normalisedComponents = model.components_ / model.components_.sum(axis=1)[:, np.newaxis]


    # TODO: complete the implementation

    #
    # Answer: Wordcloud
    #

    topicNum = len(model.components_)
    # number of wordclouds for each row
    plotColNum = 3
    # number of wordclouds for each column
    plotRowNum = int(math.ceil(topicNum / plotColNum))

    for topicId, lTopicDist in enumerate(normalisedComponents):
        lWordProb = {featureNames[i] : wordProb for i,wordProb in enumerate(lTopicDist)}
        wordcloud = WordCloud(background_color='black')
        wordcloud.fit_words(frequencies=lWordProb)
        plt.subplot(plotRowNum, plotColNum, topicId+1)
        plt.title('Topic %d:' % (topicId+1))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

    plt.show(block=True)


#######################

if __name__ == '__main__':
    main()

