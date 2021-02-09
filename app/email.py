import requests
import datetime
from threading import Thread


class Emailer:
  def __init__(self):
    self.spreadsheet_id = None
    self.mailgun_api_token = None


  def init_app(self, app):
    self.spreadsheet_id = app.config['SPREADSHEET_ID']
    self.mailgun_api_token = app.config['MAILGUN_API_TOKEN']


  def send_async_email(self, recipient, subject, body):
    requests.post(
      "https://api.mailgun.net/v3/quietbroom.com/messages",
      auth=("api", self.mailgun_api_token),
      data={
        "from": "Rand <wblStatsRunnerRandy@quietbroom.com>",
        "to": [recipient],
        "subject": subject,
        "text": body
      }
    )


  def send_email(self, name, subject, recipient):
    body = """
  Hey {}, what's going on?

  Here's your updated stats, fresh off the press.

  https://docs.google.com/spreadsheets/d/{}/

  Hope you enjoy the rest of your {}.

  Sincerely,
  Rand
  """.format(name, self.spreadsheet_id, datetime.datetime.today().strftime('%A'))

    Thread(target=self.send_async_email, args=(recipient, subject, body)).start()


  def send_all_emails(self, players):
    for player in players:
      self.send_email(player.first_name, '2020 WBL Stats', player.email)


  def send_password_reset_email(self, name, subject, recipient, token):
    body = """
  Hey {},

  Looks like you forgot your password! Don't fret, I've got you covered. Click this link:

  https://data.quietbroom.com/password_reset/{}

  Hope you enjoy the rest of your {}.

  Sincerely,
  Rand
  """.format(name, token, datetime.datetime.today().strftime('%A'))

    Thread(target=self.send_async_email, args=(recipient, subject, body)).start()