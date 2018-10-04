from rauth import OAuth1Service
#import ujson as json
import json
import Tweet
import time
import datetime, pytz
import zipfile, io


##############
## Settings ##
##############

# Set this to "True" if you downloaded your full archive from Twitter.
DELETE_FROM_FULL_ARCHIVE = True

# This should be a <username>.taj file if DELETE_FROM_ARCHIVE is False
# This should be a twitter-YYYY-MM-DD-*.zip file if DELETE_FROM_ARCHIVE is True
#tweets_file = 'data/users/<your username>.taj'
tweets_file = 'data/users/twitter-2018-10-04-a19adcfdf74fe163c55ee32e22efdef6332e4f86c5ad9a232ffb8e4b65d930fd.zip'

# Set the newest tweet you want to delete (higher is newer)
AGE_LIMIT_NEW = float('inf')
enddate = datetime.datetime.fromtimestamp(3408135217,tz=pytz.UTC)
enddate = datetime.datetime.fromtimestamp(1388448817,tz=pytz.UTC)

# Set the oldest tweet you want to delete (lower is older)
AGE_LIMIT_OLD = 1
startdate = datetime.datetime.fromtimestamp(0,tz=pytz.UTC)

# Load Twitter API Keys
# NOTE: The API Keys must be from the account you wish to delete and
# the application must have WRITE access.
with open('secrets.json') as fin:
    secrets = json.load(fin)


print('Deleting your tweets...')


#################
## Load Tweets ##
#################

    
if DELETE_FROM_FULL_ARCHIVE:
    zipped_archive = zipfile.ZipFile(tweets_file, 'r')
    with io.TextIOWrapper(zipped_archive.open('tweet.js', 'r'), encoding='utf-8') as fin:
        d = fin.readlines()[1:]
        d = '[{'+"".join(d)
        tweets = json.loads(d)
else:
    with open(tweets_file) as fin:
        tweets = []
        for line in fin:
            try:
                tweet = json.loads(line)
                tweets.append(tweet)
            except:
                continue

print()
print(len(tweets),'tweets loaded from file. Deleting entries in range:')
print(startdate,'to',enddate)
print()


##################
## Twitter Auth ##
##################

# Twitter endpoint
ENDPOINT = 'statuses/destroy/{0}.json'

def getSession() :
    # Create rauth service
    twitter = OAuth1Service(
        consumer_key=secrets['consumer_key'],
        consumer_secret=secrets['consumer_secret'],
        name='twitter',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authorize',
        request_token_url='https://api.twitter.com/oauth/request_token',
        base_url='https://api.twitter.com/1.1/')
    
    # Get a session
    session = twitter.get_session(
        (secrets['token_key'], secrets['token_secret']))
    
    return session

with getSession() as sess:
    for tweet in tweets:
        tweet_id = Tweet.getTweetID(tweet)
        date = Tweet.getTimeStamp(tweet)
        if AGE_LIMIT_OLD < int(tweet_id) < AGE_LIMIT_NEW and \
        startdate < date < enddate :
            print(tweet_id,date,Tweet.getTweetText(tweet))
            params = {
                'id' : tweet_id
            }
            resp = sess.post(ENDPOINT.format(tweet_id),data=params)
            print(resp)
    
