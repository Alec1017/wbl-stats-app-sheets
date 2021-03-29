import slack


class SlackBot:
    def __init__(self):
        self.token = None


    def init_app(self, app):
        self.token = app.config['SLACK_TOKEN']


    def send_message(self, channel='#scripting', message=''):
        connection = slack.WebClient(token=self.token)

        return connection.chat_postMessage(channel=channel, text=message)
