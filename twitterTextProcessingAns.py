#
# COSC2671 Social Media and Network Analytics
# @author Jeffrey Chan, 2018
#

import sys
import json
import string
from collections import Counter
import nltk
import re
import matplotlib.pyplot as mpl


def main():
    """
    Pre-process tweets, including tokenisation etc, then print out the most frequent terms.
    Afterwarsds will print out the historgram of term frequencies.
    This forms the answer to tuteLab1.
    """

    # load json file
    # note usually we would do some checks, but for clarify's sake we haven't implement that code here
    # Specify the json file that we want to analyse the mentions as the first command line argument
    #   python twitterTextProcessingAns.py [json filename]
    # where as an example we can have the 'rmitCsTwitterTimeline.json"
    #   python twitterTextProcessingAns.py rmitCsTwitterTimeline.json
    fJsonName = sys.argv[1]

    # number of most frequent terms to display
    freqNum = 50


    #
    # First part of answer to filtering out hash tags, emoticons etc
    #

    # tweet tokeniser to use
    tweetTokeniser = nltk.tokenize.TweetTokenizer()
    # use the punctuation symbols defined in string.punctuation
    lPunct = list(string.punctuation)
    # use stopwords from nltk and a few other twitter specific terms like 'rt' (retweet)
    lStopwords = nltk.corpus.stopwords.words('english') + lPunct + ['rt', 'via']
    # This additional part removes single quations etc
    lStopwords.extend(['"', "'", '“', '’', '…', '”', '...'])
    # we use the popular Porter stemmer
    tweetStemmer = nltk.stem.PorterStemmer()

    # our term frequency counter
    termFreqCounter = Counter()

    # open json file and process it tweet by tweet
    with open(fJsonName, 'r') as f:
        for line in f:
            # Me: this "if" clause is added to skip blank lines between tweets.
            if line not in ['\n', '\r\n']:
                tweet = json.loads(line)
                tweetText = tweet.get('text', '')
                # tokenise, filter stopwords and get convert to lower case
                lTokens = processTweet(text=tweetText, tokenizer=tweetTokeniser, stemmer=tweetStemmer, stopwords=lStopwords)

                # update count
                termFreqCounter.update(lTokens)

    # print out most common terms
    for term, count in termFreqCounter.most_common(freqNum):
        print(term + ': ' + str(count))


    #
    # Second part to answer, to display as a graph
    #

    # construct the x and y values
    y = [count for tag, count in termFreqCounter.most_common(freqNum)]
    x = range(1, len(y) + 1)

    # use matplotlib bar chat to plot this
    mpl.bar(x, y)
    mpl.title("Term frequency distribution")
    mpl.ylabel('# of tweets with term frequency')
    mpl.xlabel('Term frequency')
    mpl.show()


######################################################


def processTweet(text, tokenizer, stemmer, stopwords):
    """
    Perform tokenisation, normalisation (lower case and stemming) and stopword and twitter keyword removal.

    @param text: tweet text
    @param tokenizer: tokeniser used.
    @param stemmer: stemmer used.
    @param stopwords: list of stopwords used

    @returns: a list of processed tokens
    """

    # covert all to lower case
    text = text.lower()
    # tokenise
    lTokens = tokenizer.tokenize(text)
    # stem (we use set to remove duplicates)
    lStemmedTokens = set([stemmer.stem(tok) for tok in lTokens])


    # regex pattern for has tags
    regexHashTags = re.compile("^#\w+")
    # regex pattern for http
    regexHttp = re.compile("^http")

    # everything after the if is a series of things to process and not include
    # if a regular expression fails to match, it returns None (so in our case if they match then we don't want to include)
    return [tok for tok in lStemmedTokens
            if tok not in stopwords and not tok.isdigit() and regexHashTags.match(tok) == None and regexHttp.match(tok) == None]


#######################################


if __name__ == '__main__':
    main()




