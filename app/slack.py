import slack

from app import app


class SlackBot:
  token = app.config['SLACK_TOKEN']
  connection = None
  channel = '#scripting'

  def __init__(self):
    self.connection = slack.WebClient(token=self.token)

  def send_message(self, channel='#scripting', message=''):
    return self.connection.chat_postMessage(
      channel=channel,
      text=message)

