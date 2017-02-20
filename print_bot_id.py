import os
from slackclient import SlackClient

BOT_NAME = 'celebbot'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

if __name__ == "__main__":
    api_call = slack_client.api_call('users.list')
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        channel_list = slack_client.api_call('channels.list', exclude_archived=1)
        for channel in channel_list['channels']:
            if channel['is_member'] == True:
                print (channel['id'])
        for user in users:
            if "name" in user and user.get('name') == BOT_NAME:
                print("Bot ID of '"+user['name']+"' is "+user.get('id'))
