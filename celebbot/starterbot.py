from .interval import Interval
import os
import time
from slackclient import SlackClient
import tweepy
import random
import time
import keys

# consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
# consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
# key = os.environ.get('TWITTER_ACCESS_TOKEN')
# secret = os.environ.get('TWITTER_TOKEN_SECRET')




auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
api = tweepy.API(auth)

# starterbot's ID as an environment variable
# BOT_ID = os.environ.get("BOT_ID")

# constants
# AT_BOT = "<@" + BOT_ID + ">"
BOT_NAME = 'celebbot'
SLASH_COMMAND = "chatwith @"
tweets = []
last_celeb_time = False
invoker = ""

# instantiate Slack & Twilio clients
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def get_bot_info():
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


def get_celeb(username, channel):
    if username.lower() == 'realdonaldtrump':
        slack_client.api_call("chat.postMessage", channel=channel, text="Oh, is that what we are doing today? Arguing? Fine.  Going to the alternate reality where he lives.  Pray for me.", as_user=True)
    else:
        slack_client.api_call("chat.postMessage", channel=channel, text="Hang on, let me get them.", as_user=True)
    global tweets
    tweets = []
    global last_celeb_time
    last_celeb_time = time.time()
    try:
        responses = tweepy.Cursor(api.user_timeline, id=username).items()
        for response in responses:
            if "http" not in response.text:
                if "RT" not in response.text:
                    tweets.append(response.text)
        print('built up '+str(len(tweets))+' tweets')
        if len(tweets) > 1:
            slack_client.api_call("chat.postMessage", channel=channel, text='Ok, I was able to get @'+username+'.  I will now be replying only to <@' +invoker+'> on behalf of them.', as_user=True)
        else:
            slack_client.api_call("chat.postMessage", channel=channel, text='¯\\_(ツ)_/¯, I am not sure I know @'+username+' or they do not have anything to say', as_user=True)
    except tweepy.TweepError:
        last_celeb_time = 0
        slack_client.api_call("chat.postMessage", channel=channel, text='¯\\_(ツ)_/¯, looks like @'+username+' is not available', as_user=True)



def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    global invoker
    response = False
    if command.startswith(SLASH_COMMAND):
        timer = time.time() - last_celeb_time
        if timer > 60:
            invoker = user
            requested_celeb = command[10:]
            print(requested_celeb+ ' requested')
            get_celeb(requested_celeb, channel)
        else:
            slack_client.api_call("chat.postMessage", channel=channel, text="Sorry, you have to wait "+str(round(60-timer))+" more seconds", as_user=True)
    # response = "this is where an API return would be"
    if tweets and invoker:
        if not command.startswith("<@"):
            response = random.choice(tweets);
    # response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    while response:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = False


def parse_slack_output(slack_rtm_output, BOT_ID):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print(output)
            if output and 'text' in output and 'user' in output and BOT_ID not in output['user']:
                return output['text'], output['channel'], output['user']
            # if output and 'text' in output and AT_BOT in output['text']:
            #     # return text after the @ mention, whitespace removed
            #     return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None, None


# if __name__ == "__main__":
#     BOT_ID, channel_in = get_bot_info()
#     READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
#     if slack_client.rtm_connect() and BOT_ID and channel_in:
#         print("StarterBot connected and running!")
#         slack_client.api_call("chat.postMessage", channel=channel_in, text="CelebBot running, type chatwith <celeb twitterhandle here. ex: @twitter> to chat with that celeb.  This can only happen once a minute", as_user=True)
#         def check_socket():
#             command, channel, user = parse_slack_output(slack_client.rtm_read())
#             if command and channel and user:
#                 handle_command(command, channel, user)
#             time.sleep(READ_WEBSOCKET_DELAY)
#         tick = Interval(check_socket)
#     else:
#         print("Connection failed. Invalid Slack token or bot ID?")
