from setuptools import setup

setup(
    name='Twitter Miner',
    version='0.0.1',
    url='',
    packages=['twitter_miner'],
    package_data = {'twitter_miner': ['secret.json']},
    license='MIT',
    author='Scott Doucet',
    author_email='duroktar@gmail.com',
    description='',
    install_requires=["marshmallow", "arrow", "tweepy", "requests", "oauthlib"],
    entry_points={
          'console_scripts': [
              'twitmine = twitter_miner.__main__:twitter',
              'twitmine-config = twitter_miner.__main__:config'
          ]
      }
)