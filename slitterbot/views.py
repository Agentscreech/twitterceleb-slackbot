from django.shortcuts import render, redirect
from slitterbot.starterbot import *
import json
from pymongo import MongoClient
# from .twitter_auth import auth_twitter
from django.http import *


#mongodb stuff

mongo = MongoClient()
db = mongo.bot_database

# Create your views here.

def index(request):
  if request.method == "GET":
    return render(request, 'slitterbot/index.html')
  if request.method == "POST":
      if 'start_bot' in request.POST:
        is_running = start_bot(request.POST['bot_name'])
      elif 'stop_bot' in request.POST:
        is_running = stop_bot(request.POST['bot_name'])
      context = {
        'bot': is_running
      }
      return render(request, 'slitterbot/add_bot.html',context)


def start_bot(bot_name):
  BOT_ID, channel_in = get_bot_info(bot_name)
  if slack_client.rtm_connect() and BOT_ID and channel_in:
    print("SlitterBot connected and running!")
    slack_client.api_call("chat.postMessage", channel=channel_in, text="SlitterBot running, type chatwith <celeb twitterhandle here. ex: @twitter> to chat with that celeb.  This can only happen once a minute", as_user=True)
    def check_socket():
            command, channel, user = parse_slack_output(slack_client.rtm_read(), BOT_ID)
            if command and channel and user:
                handle_command(command, channel, user)
    is_running = db.bot_database.find_one_and_update({'name': bot_name},{"$set":{'bot_running': True}}, return_document=ReturnDocument.AFTER)
    Interval(check_socket)
  else:
        print("Connection failed. Invalid Slack token or bot ID?")
  return is_running

def stop_bot(bot_name):
  db.bot_database.find_one_and_update({'name': bot_name},{ "$set": {'bot_running': False}}, return_document=ReturnDocument.AFTER)
  BOT_ID, channel_in = get_bot_info()
  slack_client.api_call("chat.postMessage", channel=channel_in, text="SlitterBot powering down...", as_user=True)
  return False

def add_twitter(request):
  bot_name = request.GET['bot_name']
  print(bot_name, request.GET['slack_token'])
  bot_check = db.bot_database.find({'name':bot_name})
  print(bot_check.count())
  for item in bot_check:
    print('trying to print',item)

  if bot_check.count() == 0:
        db.bot_database.insert_one({'name':bot_name,'slack_token':request.GET['slack_token']})
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "http://localhost:8000/bot/add")
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print('Error! Failed to get rquest token')
        request.session['request_token'] = auth.request_token
        request.session['slack_token'] = request.GET['slack_token']
        request.session['bot_name'] = bot_name
        response = HttpResponseRedirect(redirect_url)
        return response
  else:
    context = {'create_message': 'That Bot already exists'}
    return render(request, 'slitterbot/index.html',
    context)


def add_bot(request):
    if request.method == "GET":
      oauth_token = request.GET['oauth_token']
      oauth_verifier = request.GET['oauth_verifier']
      if oauth_token is None:
        return render('slitterbot/error.html')
      request_token = request.session.get('request_token')
      bot_name = request.session.get('bot_name')
      if request_token is None:
        return render('slitterbot/error.html')
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.request_token = request_token
      try:
          auth.get_access_token(oauth_verifier)
          user_token = {'access_token': auth.access_token,
          'access_token_secret': auth.access_token_secret}
          db.bot_database.find_one_and_update({"name":bot_name},{"$set":user_token})
      except tweepy.TweepError:
          # Failed to get access token
          return render(request, 'slitterbot/error.html')
    print(bot_name)
    return render(request, 'slitterbot/bot_panel.html',{'bot_name':bot_name})

# def auth_twitter(request):
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "http://localhost:8000/bot/add")
#     try:
#         redirect_url = auth.get_authorization_url()
#     except tweepy.TweepError:
#         print('Error! Failed to get rquest token')
#     request.session['request_token'] = auth.request_token
#     response = HttpResponseRedirect(redirect_url)
#     return response


def error(request):
  pass
