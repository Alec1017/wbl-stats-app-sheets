import slack

from app import slack_token


class SlackBot:
  token = slack_token
  connection = None
  channel = '#scripting'

  def __init__(self):
    self.connection = slack.WebClient(token=self.token)

  def send_message(self, channel='#scripting', message=''):
    return self.connection.chat_postMessage(
      channel=channel,
      text=message)

