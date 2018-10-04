from rauth import OAuth1Service
import ujson as json
import Tweet
import time
import datetime, pytz

##############
## Settings ##
##############

print('Acquiring data...')

# List users to collect
USERNAMES = [
    'backhack_detect'
]

# Load Twitter API Keys
with open('secrets.json') as fin:
    secrets = json.load(fin)

# Set the oldest tweet you want to collect (lower is older)
AGE_LIMIT = 1
startdate = datetime.datetime.fromtimestamp(100,tz=pytz.UTC)

# Set the number of queries you want to use (max 180)
# Careful, you only get 180 every 15 minutes!
# You can only collect up to 3200 tweets from a user, and each query collects up to 200
# tweets, so 20 should be more than enough for a single user, even if some queries
# come up with fewer than 200 results. (Twitter API is a little quirky like that.)
NUM_QUERIES = 2

# Set to "False" to disinclude native retweets this user has made
include_rts = True

##################
## Twitter Auth ##
##################

# Twitter endpoint
ENDPOINT = 'statuses/user_timeline.json'

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


#####################
## Collection Loop ##
#####################
while True :
    try :
        for user in USERNAMES :
            print('\nCollecting ' + user,end='',flush=True)
            ctr = NUM_QUERIES
            newest_tweet = -1
            oldest_tweet = -1
            # Auth a session to Twitter
            with getSession() as sess, open('data/users/'+user+'.taj','a+') as fout :
                
                # While we're allowed to collect more tweets
                while ctr > 0 :
                    
                    # We've used one request from our rate-limit
                    ctr -= 1
                    
                    # Update collection bounds
                    tweet_bounds = {
                        'tweet_mode' : 'extended',
                        'screen_name' : user,
                        'count' : '200',
                        'since_id' : str(AGE_LIMIT),
                        'include_rts' : include_rts
                    }
                    if oldest_tweet > 0 :
                        tweet_bounds['max_id'] = oldest_tweet - 1
                    
                    # Send our request
                    resp = sess.get(ENDPOINT, params=tweet_bounds)
                    print('.',end='',flush=True)
                    # Catch bad JSON
                    try :
                        data = resp.json()
                    except :
                        print('\nError decoding JSON.')
                        continue
                    
                    # Check for rate limit
                    if resp.status_code == 429 :
                        print('\nRate-limited. Did you wait 15 minutes?')
                        time.sleep(60.0)
                        ctr += 1
                        continue
                    
                    # Parse dates, find oldest tweet
                    for tweet in data :
                        
                        tweetdate = Tweet.getTimeStamp(tweet)
                        if tweetdate is None :
                            print('\nCollection failed for ' + user)
                            ctr = 0
                            break
                        if tweetdate < startdate and ctr > 0 :
                            print('\nCompleted collection for ' + user)
                            ctr = 0
                        
                        # Update our oldest tweet
                        if oldest_tweet < 0 or 'id' in tweet \
                                and tweet['id'] is not None \
                                and tweet['id'] < oldest_tweet :
                            oldest_tweet = tweet['id']
                        
                        # Update our newest tweet
                        if newest_tweet < 0 or 'id' in tweet \
                                and tweet['id'] is not None \
                                and tweet['id'] > newest_tweet :
                            newest_tweet = tweet['id']
                        
                        # Parse tweet
                        fout.write(json.dumps(tweet) + '\n')
                        
                
        # When you've finished the list, exit
        break
    
    # If something breaks start a fresh connection
    except ConnectionError :
        continue

