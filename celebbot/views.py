from django.shortcuts import render, redirect
from celebbot.starterbot import *
import json
from pymongo import MongoClient
# from .twitter_auth import auth_twitter
from django.http import *


#mongodb stuff

mongo = MongoClient()
db = mongo.bot_database
db.drop_collection('is_running')

# Create your views here.

def index(request):
  if request.method == "GET":
    return render(request, 'celebbot/index.html')
  if request.method == "POST":
      if 'start_bot' in request.POST:
        is_running = start_bot()
      elif 'stop_bot' in request.POST:
        is_running = stop_bot()
      context = {
        'bot': is_running
      }
      return render(request, 'celebbot/index.html',context)


def start_bot():
  BOT_ID, channel_in = get_bot_info()
  # READ_WEBSOCKET_DELAY = 1
  if slack_client.rtm_connect() and BOT_ID and channel_in:
    print("StarterBot connected and running!")
    slack_client.api_call("chat.postMessage", channel=channel_in, text="CelebBot running, type chatwith <celeb twitterhandle here. ex: @twitter> to chat with that celeb.  This can only happen once a minute", as_user=True)
    def check_socket():
            command, channel, user = parse_slack_output(slack_client.rtm_read(), BOT_ID)
            if command and channel and user:
                handle_command(command, channel, user)
            # time.sleep(READ_WEBSOCKET_DELAY)
    Interval(check_socket)
    is_running = db.is_running.insert_one({'bot_running': True}).inserted_id
  else:
        print("Connection failed. Invalid Slack token or bot ID?")
  return is_running

def stop_bot():
  db.drop_collection('is_running')
  BOT_ID, channel_in = get_bot_info()
  slack_client.api_call("chat.postMessage", channel=channel_in, text="CelebBot powering down...", as_user=True)
  return False

def add_twitter(request):
  response = auth_twitter(request)
  return response

def add_bot(request):
    if request.method == "GET":
      print('request from twitter',request.GET["oauth_verifier"])
      oauth_token = request.GET['oauth_token']
      print('oauth_token', oauth_token)
      oauth_verifier = request.GET['oauth_verifier']
      print('oauth_verifier', oauth_verifier)
      if oauth_token is None:
        return render('celebbot/error.html')
      request_token = request.session.get('request_token')
      print('request_token', request_token)
      if request_token is None:
        return render('celebbot/error.html')
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.request_token = request_token
      print(auth.request_token)
      try:
          auth.get_access_token(oauth_verifier)
      except tweepy.TweepError:
          # Failed to get access token
          return render(request, 'celebbot/error.html')
    return render(request, 'celebbot/add_bot.html')

def auth_twitter(request):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "http://localhost:8000/bot/add")
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get rquest token')
    request.session['request_token'] = auth.request_token
    response = HttpResponseRedirect(redirect_url)
    return response


def error(request):
  pass
