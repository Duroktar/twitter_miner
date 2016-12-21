from __future__ import print_function
import os, sys
import json
import tweepy
import webbrowser
import itertools
import pickle

from datetime import date
from marshmallow import Schema, fields, pprint

from operator import itemgetter
# import maya
import arrow


PATH = os.path.dirname(os.path.realpath(__file__))

def load_config(target):
    with open(target) as f:
        return json.loads(f.read())

def save_config(config, target):
    with open(target, 'w') as f:
        json.dump(config, f)

CONFIG_FILE = os.path.join(PATH, 'secret.json')
CONFIG = load_config(CONFIG_FILE)

try:
    CONSUMER_TOKEN = CONFIG.get('TOKEN', None)
    CONSUMER_SECRET = CONFIG.get('SECRET', None)
    if not all([CONSUMER_TOKEN, CONSUMER_SECRET]):
        CONSUMER_TOKEN = raw_input("Copy and paste your Twitter Consumer `Token` here  > ")
        CONSUMER_SECRET = raw_input("Copy and paste your Twitter Consumer `Secret` here > ")
        CONFIG['TOKEN'] = CONSUMER_TOKEN
        CONFIG['SECRET'] = CONSUMER_SECRET
        save_config(CONFIG, CONFIG_FILE)
except Exception as e:
    print(e)


AUTH_KEY = CONFIG.get('auth_key', None)
AUTH_SECRET = CONFIG.get('auth_secret', None)


auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)

if AUTH_KEY is None or AUTH_SECRET is None:
    print("First login - ")
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    
    print(" - Opening browser - ")
    webbrowser.open(redirect_url)

    REQUEST_TOKEN = auth.request_token

    verifier = raw_input('Verifier: ')
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')
    CONFIG['auth_key'] = auth.access_token 
    CONFIG['auth_secret'] = auth.access_token_secret
    save_config(CONFIG, CONFIG_FILE)


auth.set_access_token(AUTH_KEY, AUTH_SECRET)


api = tweepy.API(auth, wait_on_rate_limit=True,
				   wait_on_rate_limit_notify=True)
 
print("Logged in!")

######
# For helping with the rate_limiter ##
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)


class TweetSchema(Schema):
    id = fields.UUID()
    author = fields.Str()
    text = fields.Str()
    favorite_count = fields.Int()
    favorited = fields.Bool()
    created_at = fields.Date()
    retweet_count = fields.Int()
    retweeted = fields.Bool()

# Don't use this one. It's buggy and can crash your pc
# def get_user_tweets(username, items):
#     statuses = []
#     for status in tweepy.Cursor(api.user_timeline, id=username).items(items):
#         tweet = dict(
#             id = status.id,
#             author = status.user.screen_name,
#             text = status.text,
#             favorite_count = status.favorite_count,
#             favorited = status.favorited,
#             created_at = status.created_at,
#             # author = status.author,
#             retweeted = True if status.get('retweeted_status') else False,
#             # user = status.user,
#             # in_reply_to_screen_name = status.in_reply_to_screen_name,
#             # meta = status,
#             retweet_count = status.retweet_count)
#         statuses.append(tweet)
#     yield statuses

def get_weeks_update_on_user(who):
    statuses = []
    schema = TweetSchema()

    # yesterday = maya.when('yesterday').datetime().strftime("%Y-%m-%d")
    # last_week = maya.when('last week').datetime().strftime("%Y-%m-%d")
    last_week = arrow.utcnow().replace(weeks=-1).format("YYYY-MM-DD")

    query = "from:{}".format(who)

    search = api.search(q=query,since=last_week, count=100)
    for status in search:
        retweeted = True if 'retweeted_status' in vars(status) else False
        tweet = dict(
            id = status.id,
            author = status.user.screen_name,
            text = status.text.encode('utf-8'),
            favorite_count = status.favorite_count,
            favorited = status.favorited,
            created_at = status.created_at,
            retweeted = retweeted,
            retweet_count = status.retweet_count)
        statuses.append(schema.dump(tweet))
    return statuses

def process_user(username):
    search = username

    # today = maya.when('today').datetime().strftime('%Y-%d-%m')
    today = arrow.utcnow().format("YYYY-DD-MM").encode('utf-8')
    log_file = search + "-" + today + ".log"


    if not os.path.isfile(log_file):

        test = get_weeks_update_on_user(search)
        data = [i.data for i in test]
        sorted_data = reversed(sorted(data, key=itemgetter('favorite_count', 'retweet_count')))

        table_data = []
        for i in sorted_data:
            tweet = i
            stars = "-" * 60
            time = arrow.get(tweet['created_at']).humanize()  #  maya.parse(tweet['created_at']).slang_time()
            filler = str(tweet['text'].encode('utf-8'))
            template = "{}\nAuthor - {}\nTime - {}\nFavorited - {}\nRetweeted - {}\nTweet - {}\n{}".format(stars, tweet['author'], time, tweet['favorite_count'], tweet['retweet_count'], filler, stars)
            table_data.append(template)

        with open(log_file, 'w') as log:
            log.write(" ".join([i for i in table_data]))
        print("Done. Log written to file - {}".format(log_file))
    else:
        print("Already got that info today. To avoid being rate limited wait 15 minutes before trying again and delete the log file for that user for today.")

def twitter():
    who = raw_input("Who would you like to search? $ ") or None
    if who is None:
        print("Goodbye.")
        sys.exit()
    process_user(who)

if __name__ == '__main__':
    twitter()
