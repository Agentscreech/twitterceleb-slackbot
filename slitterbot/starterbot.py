from .interval import Interval
import os
import time
from slackclient import SlackClient
import tweepy
import random
import time
from .keys import *
from pymongo import MongoClient
from pymongo import ReturnDocument
mongo = MongoClient()
db = mongo.bot_database

# consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
# consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
# key = os.environ.get('TWITTER_ACCESS_TOKEN')
# secret = os.environ.get('TWITTER_TOKEN_SECRET')
# # auth.set_access_token(key, secret)

# starterbot's ID as an environment variable
# BOT_ID = os.environ.get("BOT_ID")

# constants
SLASH_COMMAND = " chatwith @"

# instantiate Slack & Twilio clients
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def get_bot_info(BOT_NAME, slack_token):
    slack_client=SlackClient(slack_token)
    channel_in = ""
    api_call = slack_client.api_call('users.list')
    if api_call.get('ok'):
      # retrieve all users so we can find our bot
      channel_list = slack_client.api_call('groups.list', exclude_archived=1)
      for group in channel_list['groups']:
          channel_in = group['id']
          print('bot in channel/group',channel_in)
      if not channel_in:
        channel_list = slack_client.api_call('channels.list', exclude_archived=1)
        for channel in channel_list['channels']:
          if channel['is_member']:
            channel_in = channel['id']
      print('bot in channel ', channel_in)
      users = api_call.get('members')
      for user in users:
          if "name" in user and user.get('name') == BOT_NAME:
              print("Bot ID of '"+user['name']+"' is "+user.get('id'))
              BOT_ID = user.get('id')
    return BOT_ID, channel_in


def get_celeb(username, channel,slack_client):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    #TODO still need to use the user's twitter token
    if username.lower() == 'realdonaldtrump':
        slack_client.api_call("chat.postMessage", channel=channel, text="Oh, is that what we are doing today? Arguing? Fine.  Going to the alternate reality where he lives.  Pray for me.", as_user=True)
    else:
        slack_client.api_call("chat.postMessage", channel=channel, text="Hang on, let me get them.", as_user=True)
    tweets = []
    existing_users = db.twitter_users.find_one({'user':username})
    if existing_users is not None:
        for users in existing_users:
            if user == username:
                tweets = existing_users['tweets']
    if len(tweets) == 0:
        try:
            responses = tweepy.Cursor(api.user_timeline, id=username).items()
            for response in responses:
                if "http" not in response.text:
                    if "RT" not in response.text:
                        tweets.append(response.text)
            db.twitter_users.insert_one({'user':username,'tweets':tweets})
            print('built up '+str(len(tweets))+' tweets')
            if len(tweets) > 1:
                slack_client.api_call("chat.postMessage", channel=channel, text='Ok, I was able to get @'+username+'. Mention me and I will responed on behalf of them.', as_user=True)
            else:
                slack_client.api_call("chat.postMessage", channel=channel, text='¯\\_(ツ)_/¯, I am not sure I know @'+username+' or they do not have anything to say', as_user=True)
        except tweepy.TweepError:
            last_celeb_time = 0
            slack_client.api_call("chat.postMessage", channel=channel, text='¯\\_(ツ)_/¯, looks like @'+username+' is not available', as_user=True)
    else:
        slack_client.api_call("chat.postMessage", channel=channel, text='Ok, I was able to get @'+username+'. Mention me and I will responed on behalf of them.', as_user=True)



def handle_command(command, channel,slack_client):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    active_slack = db.slack_channel.find_one_and_update({'channel':channel}, {'$set':{'channel':channel}}, upsert=True,return_document=ReturnDocument.AFTER)
    response = False
    print(active_slack)
    if 'celeb' in active_slack:
        active_user = db.twitter_users.find_one({'user':active_slack['celeb']})
        tweets = active_user['tweets']
    else:
        tweets = []
    if command.startswith(SLASH_COMMAND):
        timer = 70
        if timer > 60:
            requested_celeb = command[11:]
            if 'celeb' in active_slack:
                if active_slack['celeb'] ==     requested_celeb:
                    requested_celeb = db.twitter_users.find_one({'user':requested_celeb})
                    tweets = requested_celeb['tweets']
                    slack_client.api_call("chat.postMessage", channel=channel, text='Ok, I was able to get @'+requested_celeb['user']+'. Mention me and I will responed on behalf of them.', as_user=True)
            else:
                print(requested_celeb+ ' requested')
                db.slack_channel.find_one_and_update({'channel':channel}, {"$set":{'celeb':requested_celeb,'last_celeb_time':time.time()}})
                get_celeb(requested_celeb, channel, slack_client)
        else:
            slack_client.api_call("chat.postMessage", channel=channel, text="Sorry, you have to wait "+str(round(60-timer))+" more seconds", as_user=True)

    if tweets:
        response = random.choice(tweets);
    while response:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = False


def parse_slack_output(slack_rtm_output, BOT_ID):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print(output)
            if output and 'text' in output and 'user' in output and BOT_ID not in output['user']:
                AT_BOT = "<@" + BOT_ID + ">"
                return output['text'].split(AT_BOT)[1], output['channel']
    return None, None


# if __name__ == "__main__":
