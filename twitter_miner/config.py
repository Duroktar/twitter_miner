import os, sys
import json
import time

PATH = os.path.dirname(os.path.realpath(__file__))
SECRET_PATH = os.path.join(os.path.expanduser("~"), '.twitmine')

def load_config(target):
    with open(target) as f:
        return json.loads(f.read())

def save_config(config, target):
    with open(target, 'w') as f:
        json.dump(config, f)

CONFIG_FILE = os.path.join(SECRET_PATH, 'secret.json')
CONFIG = load_config(CONFIG_FILE)

def config():
    CONSUMER_TOKEN = raw_input("Copy and paste your Twitter Consumer `Token` here  > ")
    CONSUMER_SECRET = raw_input("Copy and paste your Twitter Consumer `Secret` here > ")
    print("Finished")
    time.sleep(5)
    sys.exit()