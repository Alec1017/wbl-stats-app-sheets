import slack
from flask import current_app


def send_message(channel='#scripting', message=''):
  with current_app._get_current_object().app_context():
    connection = slack.WebClient(token=current_app.config['SLACK_TOKEN'])

    return connection.chat_postMessage(
      channel=channel,
      text=message)
