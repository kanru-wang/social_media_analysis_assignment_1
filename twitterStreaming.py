import sys
import string
import time
from tweepy import Stream
from tweepy.streaming import StreamListener
from twitterClient import twitterAuth


def main():
    """
    Usage: twitterSentiment.py [out filename (json)] <list of query terms>
    Example:
    python twitterSentiment.py outAbc.json rmit #rmit_csit cs
    To gather tweets that have keywords "rmit", "#rmit_csit", "cs"

    To stop collecting, just stop the script.
    Me: to stop collecting, just shut down the IDE.
    """
    # read in from command line all the terms that we will filter the stream on
    assert(len(sys.argv) > 2)
    sOutFilename = sys.argv[1]
    sQuery = sys.argv[2:]

    # output file is the input file name with all the query terms and '.txt'
    auth = twitterAuth()
    # open up the stream
    twitterStream = Stream(auth, CustomListener(sOutFilename))
    # filter out tweets not of query word
    twitterStream.filter(track=sQuery, async=True)


# Me: CustomListener inherits StreamListener
#     StreamListener is not constructed (probably doesn't require construction)
#     on_data and on_error are functions from StreamListener, but overridden.
class CustomListener(StreamListener):
    """
    Listener that calls on_data when a new tweet appears.
    """


    def __init__(self, fName):
        self.outFile = fName
        self.timeToSleep = 10


    def on_data(self, raw_data):
        try:
            with open(self.outFile, 'a') as f:
                f.write(raw_data)
                return True

        except BaseException as e:
            sys.stderr.write("Error on_data: {}\n.format(e)")
            time.sleep(self.timeToSleep)

        return True


    def on_error(self, status):
        if status == 420:
            sys.stderr.write("Rate limit exceeded\n")
            return False
        else:
            sys.stderr.write("Error {}\n".format(status))
            return True


def format_filename(fName):
    """
    Conver all irrelevant characters from the input filename.
    """
    lValidChars = "-_." + string.ascii_letters + string.digits

    return ''.join(oneChar for oneChar in fName for oneChar in lValidChars)



if __name__ == '__main__':
    main()