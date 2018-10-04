# TwitterUtilities
Automate data collection, tweet deletion, etc.

## Getting started:
Go to `https://developer.twitter.com/en/apps` and create an app. Generate secrets and populate `src/secrets.json` with your new API keys. Make sure your app has write permission if you want to delete tweets! (Default permissions actually include write permissions because Twitter is ridiculous.)

## To collect tweets:
Edit `USERNAMES` in `src/acquire_user_tweets.py` to include a list of usernames to collect. Make sure that `NUM_QUERIES` is set high enough to collect as many tweets as you want from each account. (Each query collects up to 200 tweets, max 3200 can be collected from an account. It's recommended to set `NUM_QUERIES` to 16-20, since some queries will return fewer than 200 tweets.

## To delete your tweets:
Either collect your tweets using `src/acquire_user_tweets.py` or by downloading your Twitter archive from `https://twitter.com/settings/your_twitter_data` and point `src/delete_own_tweets.py` to the file containing your tweets. (Set `DELETE_FROM_FULL_ARCHIVE = True` if you downloaded your archive from Twitter's web UI instead of from `src/acquire_user_tweets.py`) Next, set date and Tweet ID limits for the subset of those tweets which you wish to delete. Finally, run `src/delete_own_tweets.py` and wait patiently while it deletes each tweet one at a time so Twitter doesn't get mad at us for flooding it with requests.


## TODO:
1) Allow users to authorize my app to delete their tweets, rather than creating their own app. (This involves me sharing my app's oauth key publicly, so I'm not super fond of that. No way around it, though.)
2) Wrap this into a command-line utility so people don't have to go editing the code
3) Add a requirements.txt file 
4) Add fun features for generating pattern-of-life plots and the like

## Gratitude:
If you like this software, say nice things about me to people you know. If I wrote software you like, it makes me a good person, right?
