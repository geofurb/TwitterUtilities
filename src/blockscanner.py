from rauth import OAuth1Service
import ujson as json
import time

# Resume where we left off (from the beginning if no output stored)
RESUME = True

# Don't scan verified users
SKIP_VERIFIED = True

# Output filename
OUTPUT = 'blockscan_results.txt'

last_id = None
with open(f'data/{OUTPUT}') as fin:
    for line in fin:
        line = line.strip()
        if line and line != 'ID':
            last_id = int(line.split('\t')[0])

# Load Twitter API Keys
with open('secrets.json') as fin:
    secrets = json.load(fin)


def getSession():
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

ACCOUNT = 'account/verify_credentials.json'
FOLLOWERS = 'followers/ids.json'
BLOCKS = 'blocks/ids.json'
LOOKUP = 'users/lookup.json'
FRIENDS = 'friends/ids.json'

with getSession() as sess, open(f'data/{OUTPUT}', 'w+') as fout:
    # Verify credentials
    print('Verifying credentials...', end='\t', flush=True)
    try:
        resp = sess.get(ACCOUNT)
        data = resp.json()
        my_id = data['id']
    except:
        print('Bad credentials')
        raise
    print('Done!')

    # Get blocked users
    print('Tabulating blocked users...', end='\t', flush=True)
    resp = sess.get(BLOCKS)
    data = resp.json()
    blocked_users = set(data["ids"])
    print('Done!')

    # Get own followers
    print('Tabulating followers...', end='\t', flush=True)
    followers = []
    cursor = -1             # Iterate pages in case more than 5000 followers
    while cursor != 0:
        resp = sess.get(FOLLOWERS, params={'user_id': my_id, 'cursor': cursor})
        data = resp.json()
        followers.extend(data['ids'])
        cursor = data['next_cursor']
    print('Done!')

    # Saturate info on followers, sort low-to-high by friends
    print('Acquiring follower metadata...', end='\t', flush=True)
    users = []
    for follower in [followers[i:i+100] for i in range(0, len(followers), 100)]:    # chunk followers into 100's
        for attempt in range(3):
            try:
                resp = sess.post(LOOKUP, data={'user_id': ','.join([str(x) for x in follower]), 'include_entities': False})
                data = resp.json()
                for user in data:
                    users.append((user['id'], user['screen_name'], user['verified'], user['friends_count'], user['followers_count']))
                break
            except:
                if attempt == 2:
                    print(f'\nThere was a problem getting the metadata for some followers. Skipping these:\n{follower}')

    print('Done!')

    # Get friends of each follower, count matches from your blocked users
    print('Tabulating blocked friends for each of your followers. This might take a long time.')
    users = sorted(users, key=lambda x:x[3])
    if last_id is not None:
        fout.write('ID\tUSERNAME\tBLOCKED FRIENDS\tFRIENDS\tFOLLOWERS\tVERIFIED\n')
        users = users[([x[0] for x in users]).index(last_id):]
        print(f'Resuming with {users[0][1]}.')
    print('ID\tUSERNAME\tBLOCKED FRIENDS\tFRIENDS\tFOLLOWERS\tVERIFIED')
    for user in users:
        for attempt in range(3):
            try:
                t_begin = time.time()
                resp = sess.get(FRIENDS, params={'user_id': user[0]})
                data = resp.json()
                blocked_friends = len(blocked_users.intersection(data['ids']))  # Count the number of their friends that you've blocked
                fout.write(f'{user[0]}\t{user[1]}]t{blocked_friends}\t{user[3]}\t{user[4]}\t{user[2]}\n')
                print(f'{user[0]}\t{user[1]}]t{blocked_friends}\t{user[3]}\t{user[4]}\t{user[2]}')
                time.sleep(max(0.0, 60.0 + t_begin - time.time()))
                break
            except:
                if attempt == 2:
                    print(f'There was a problem getting the first 5000 followers for {user[0]} (@{user[1]}). Skipping them.')
    print('Done tabulating blocked friends for each of your followers.')

print('End of line.')
