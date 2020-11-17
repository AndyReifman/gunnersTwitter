#!/usr/bin/python3
# -*- coding: utf-8 -*-

import praw,json,requests,tweepy,time,os,urllib.parse,datetime
from glob import glob

f = open('/home/andy/twitter/access.txt')
CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET = f.readline().split('||',4)
f.close
SUBREDDIT_TO_MONITOR='gunners'
IMAGE_DIR = 'img'
POSTED_CACHE = 'posted_posts.txt'
TWEET_MAX_LEN = 240

def getTimestamp():
    dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
    hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
    min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
    t = '[' + hr + ':' + min + '] '
    return dt + t


def strip_title(title, num_characters):
    if len(title) <= num_characters:
        return title
    else:
        return title[:num_characters-1] + "..."

def connection(subreddit):
    try:
        f = open('/home/andy/twitter/login.txt')
        user_agent,id,secret,refresh = f.readline().split('||',4)
        f.close()
        r = praw.Reddit(client_id=id,
             client_secret=secret,
             refresh_token=refresh.strip(),
             user_agent=user_agent)
        print(getTimestamp() + "OAuth session opened as /u/" + r.user.me().name)
    except Exception as e:
        print(getTimestamp() + str(e))
        print(getTimestamp() + "Setup error in Results \n")
        exit()

    subreddit = r.subreddit(subreddit)
    return subreddit

def create_tweets(subreddit_info):
    post_dict = {}
    post_ids = []
    print(getTimestamp() + "[bot] Getting posts from Reddit")
    for submission in subreddit_info.hot(limit=5):
        if submission.score >= 50 and not already_tweeted(submission.id):
            post_dict[submission.title] = {}
            post = post_dict[submission.title]
            post_ids.append(submission.id)
            post['link'] = 'https://redd.it/'+submission.id
            post['img_path'] = get_image(submission.url)
    return post_dict,post_ids


def already_tweeted(post_id):
    found = False
    with open(POSTED_CACHE, 'r') as f:
        for line in f:
            if post_id in line:
                found = True
                break
    return found

def get_image(img_url):
    if 'imgur.com' in img_url:
        file_name = os.path.basename(urllib.parse.urlsplit(img_url).path)
        img_path = IMAGE_DIR + '/' + file_name
        resp = requests.get(img_url,stream=True)
        if resp.status_code == 200:
            with open(img_path, 'wb') as image_file:
                for chunk in resp:
                    image_file.write(chunk)
            return img_path
        else:
            print(getTimestamp() + '[bot] Image failed to download. Status code: ' + resp.status_code)
    else:
        print(getTimestamp() + '[bot] Post doesn\'t point to an i.imgur.com link')
    return ''

def tweeter(post_dict, post_ids):
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET.strip())
    api = tweepy.API(auth)

    for post,post_id in zip(post_dict,post_ids):
        img_path = post_dict[post]['img_path']

        extra_text = ' ' + post_dict[post]['link'] 
        extra_text_len = 1 
        if img_path:  # Image counts as a link
            extra_text_len += T_CO_LINKS_LEN
        post_text = strip_title(post, TWEET_MAX_LEN - extra_text_len) + extra_text
        print(getTimestamp() + '[bot] Posting this link on Twitter')
        print(getTimestamp(), post_text)
        if img_path:
            print(getTimestamp() + '[bot] With image ' + img_path)
            api.update_with_media(filename=img_path, status=post_text)
        else:
            api.update_status(status=post_text)
        log_tweet(post_id)

def log_tweet(post_id):
    with open(POSTED_CACHE, 'a') as f:
        f.write(str(post_id) + '\n')

def main():
    ''' Runs through the bot posting routine once. '''
    # If the tweet tracking file does not already exist, create it
    if not os.path.exists(POSTED_CACHE):
        with open(POSTED_CACHE, 'w'):
            pass
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    subreddit = connection(SUBREDDIT_TO_MONITOR)
    post_dict, post_ids = create_tweets(subreddit)
    tweeter(post_dict, post_ids)

    # Clean out the image cache
    for filename in glob(IMAGE_DIR + '/*'):
        os.remove(filename)

if __name__ == '__main__':
    main()
