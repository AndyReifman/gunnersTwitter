# Automatic Tweeter Bot

## Table of Contents
* [General Info](#general-info)
* [Requirements](#requirements)
* [Setup](#setup)

## General Info
This is a simple script that goes and grabs 5 posts from the "hot" queue in the /r/gunners subreddit and posts them to the subreddit twitter account.

We keep track of tweets we have posted before to avoid repeats.


## Requirements
You will need a reddit account and a twitter account. You will also need to install the praw and tweepy python modules. 
`pip install praw`
`pip install tweepy`

## Setup
First off you will need to create an app for your twitter account which can be done [here.](https://developer.twitter.com/en/apps) Make sure to take note of all the keys and secrets they give, you will need them later.
You will need two files that will contain praw (`login.txt`) and tweepy (`access.txt`) info.

#### login.txt
```user_agent||client_id||client_secret||refresh_token```

#### access.txt
```consumer_key||consumer_secret||access_token||access_token_secret```

Make sure the paths for the files are updated at `line 7` and `line 31`

Assuming you have `python3` installed you can run by simply issuing `./twitter.py`
