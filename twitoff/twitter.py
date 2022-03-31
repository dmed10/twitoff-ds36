from os import getenv
from .models import DB, Tweet, User
import tweepy
import spacy

key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(key, secret)

TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):
    try:
        twitter_user = TWITTER.get_user(screen_name=username)

        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, username=username))

        DB.session.add(db_user)

        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             user_id=db_user.id,
                             vect=tweet_vector)

            DB.session.add(db_tweet)

    except Exception as error:
        print(f'Error when processing {username}: {error}')
        raise error
    else:
        DB.session.commit()


nlp = spacy.load('my_model/')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
