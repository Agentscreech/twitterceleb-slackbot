import os
from slackclient import SlackClient

BOT_NAME = 'slitterbot'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

if __name__ == "__main__":
    api_call = slack_client.api_call('users.list')
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        channel_in = ''
        users = api_call.get('members')
        for user in users:
            if "name" in user and user.get('name') == BOT_NAME:
                print("Bot ID of '"+user['name']+"' is "+user.get('id'))
                BOT_ID=user.get('id')
        channel_list = slack_client.api_call('channels.list')
        if not channel_in:
            channel_list = slack_client.api_call('groups.list')
            print(channel_list)
