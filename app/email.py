import requests
import random
import datetime

from app import email_address, email_password, spreadsheet_id, mailgun_api_token

random_fun_facts = [
  'The first-ever documented feature film was made in Australia in 1906.',
  'A strawberry is not an actual berry, but a banana is.',
  'Cookie Monster’s real name is Sid.',
  'Elvis was originally blonde. He started dying his hair black for an edgier look. Sometimes, he would touch it up himself using shoe polish.',
  'A snail can sleep for 3 years.',
  'Jousting is the official sport in the state of Maryland.',
  'Dogs can be allergic to humans.',
  'Cows give more milk when they listen to music.',
  'Astronauts actually get taller when in space.'
]


def send_email(name, subject, to_email):
  random_index = random.randint(0, len(random_fun_facts) - 1)

  email_body = """
Hey {}, what's going on?

Here's your updated stats, fresh off the press.

https://docs.google.com/spreadsheets/d/{}/

Did you know: {}

Hope you enjoy the rest of your {}.

Sincerely,
Rand
""".format(name, spreadsheet_id, random_fun_facts[random_index], datetime.datetime.today().strftime('%A'))

  try:
    requests.post(
      "https://api.mailgun.net/v3/quietbroom.com/messages",
      auth=("api", mailgun_api_token),
      data={
        "from": "Rand <wblStatsRunnerRandy@quietbroom.com>",
        "to": [to_email],
        "subject": '{}'.format(subject),
        "text": email_body
      }
    )
  except Exception as e:
    print("something went wrong, email not sent")
    print(str(e))
