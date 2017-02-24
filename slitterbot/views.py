from django.shortcuts import render, redirect
from slitterbot.starterbot import *
import json
import os
from pymongo import MongoClient
from pymongo import ReturnDocument
# from .twitter_auth import auth_twitter
from django.http import *
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')

#mongodb stuff

mongo = MongoClient('mongodb://dbuser:dbpassword@ds161069.mlab.com:61069/heroku_p8hztrhs')
db = mongo.heroku_p8hztrhs

# Create your views here.

def index(request):
  if request.method == "GET":
    return render(request, 'slitterbot/index.html')
  if request.method == "POST":
      if 'start_bot' in request.POST:
        bot = start_bot(request.POST['start_bot'])
      elif 'stop_bot' in request.POST:
        bot = stop_bot(request.POST['stop_bot'])
      context = {
        'bot_name': bot['name'],
        'is_running': bot['bot_running']
      }
      return render(request, 'slitterbot/bot_panel.html',context)


def start_bot(bot_name):
  bot = db.bot_database.find_one({'name': bot_name})
  slack_client=SlackClient(bot['slack_token'])
  BOT_ID, channel_in = get_bot_info(bot_name, bot['slack_token'])
  if slack_client.rtm_connect() and BOT_ID and channel_in:
    print("SlitterBot connected and running!")
    slack_client.api_call("chat.postMessage", channel=channel_in, text=bot['name'] +" running, mention me and type chatwith <celeb twitterhandle here. ex: @"+bot['name']+" chatwith @twitter> to chat with that celeb.", as_user=True)
    def check_socket():
            command, channel = parse_slack_output(slack_client.rtm_read(), BOT_ID)
            if command and channel:
                handle_command(command, channel, slack_client)
    bot = db.bot_database.find_one_and_update({'name': bot_name},{"$set":{'bot_running': True}}, return_document=ReturnDocument.AFTER)
    Interval(check_socket, bot['name'])
  else:
        print("Connection failed. Invalid Slack token or bot ID?")
  return bot

def stop_bot(bot_name):
  bot = db.bot_database.find_one_and_update({'name': bot_name},{ "$set": {'bot_running': False}}, return_document=ReturnDocument.AFTER)
  slack_client=SlackClient(bot['slack_token'])
  BOT_ID, channel_in = get_bot_info(bot['name'],bot['slack_token'])
  slack_client.api_call("chat.postMessage", channel=channel_in, text=bot['name'] +" powering down...", as_user=True)
  return bot

def add_twitter(request):
  bot_name = request.GET['bot_name']
  bot_check = db.bot_database.find({'name':bot_name})
  if bot_check.count() == 0:
        db.bot_database.insert_one({'name':bot_name,'slack_token':request.GET['slack_token']})
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "https://slitterbot.herokuapp.com/bot/add")
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
    return render(request, 'slitterbot/bot_panel.html',{'bot_name':bot_name})

def get_bot(request):
    test = db.bot_database.find_one({'name': request.GET['bot_name']})
    if test is None:
      return render(request, 'slitterbot/index.html', {'get_message':"Bot not found"})
    return render(request, 'slitterbot/bot_panel.html', {'bot_name':request.GET['bot_name']})




def error(request):
  pass
