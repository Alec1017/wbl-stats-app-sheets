import requests
import datetime
from threading import Thread
from flask import current_app


def send_async_email(app, recipient, subject, body):
  with app.app_context():
    requests.post(
        "https://api.mailgun.net/v3/quietbroom.com/messages",
        auth=("api", current_app.config['MAILGUN_API_TOKEN']),
        data={
          "from": "Rand <wblStatsRunnerRandy@quietbroom.com>",
          "to": [recipient],
          "subject": subject,
          "text": body
        }
      )


def send_email(name, subject, recipient):
  body = """
Hey {}, what's going on?

Here's your updated stats, fresh off the press.

https://docs.google.com/spreadsheets/d/{}/

Hope you enjoy the rest of your {}.

Sincerely,
Rand
""".format(name, current_app.config['SPREADSHEET_ID'], datetime.datetime.today().strftime('%A'))

  Thread(target=send_async_email, args=(current_app._get_current_object(), recipient, subject, body)).start()


def send_all_emails(players):
  for player in players:
    send_email(player.first_name, '2020 WBL Stats', player.email)


def send_password_reset_email(name, subject, recipient, token):
  body = """
Hey {},

Looks like you forgot your password! Don't fret, I've got you covered. Click this link:

https://data.quietbroom.com/password_reset/{}

Hope you enjoy the rest of your {}.

Sincerely,
Rand
""".format(name, token, datetime.datetime.today().strftime('%A'))

  Thread(target=send_async_email, args=(current_app._get_current_object(), recipient, subject, body)).start()