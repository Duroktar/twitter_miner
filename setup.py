from setuptools import setup

setup(
    name='Twitter Miner',
    version='0.0.1',
    url='',
    packages=['src'],
    package_data = {'src': ['secret.json']}
    license='MIT',
    author='Scott Doucet',
    author_email='duroktar@gmail.com',
    description='',
    install_requires=["marshmallow", "arrow", "tweepy"]
)