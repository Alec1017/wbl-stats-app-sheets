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
  'Astronauts actually get taller when in space.',
  'In a pinch, olive oil can be used in place of motor oil.',
  'The last living dinosaurs were roaming the Earth around the same time that Leif Erikson stepped foot on North America.',
  'Disliking soda is correlated to having a lower overall IQ.',
  'Helen Keller once played 9 holes of golf. She shot a 60.',
  '18 percent of all FBI agents have committed at least one crime.',
  'A female buffalo is called a buffala.',
  'Due to selective breeding, modern day horses put out 1.2 horsepower instead of the normal 1 HP.',
  'Broccoli is one of three plants that can grow around active volcanoes.',
  '65 percent of Rubiks cubes purchased are of the left-handed variety.',
  'A coconut is a mammal because it grows hair and produces milk',
  'Venezuela has no escalators.',
  'Olives are just pickled grapes.',
  '3G, 4G, 5G refer to the number of satellites currently pointing at your phone.',
  'Elmo is the only fictional character to have received an official Japanese passport.',
  'Most cheap store-bought wines are just vodka diluted with water and grape juice.',
  'After multiple studies, results found that cutting a sandwich diagonally can make it appear to taste better.',
  'Lemons are just ripened limes. Hence, lemons are bigger and sometimes still have bits of green on them.',
  'Jackie Chan was given the lead role in the Mighty Ducks movie but turned it down because his failure to reach the NHL was still too fresh.',
  'The italics font is meant to represent the Leaning Tower of Pisa, thus the letters lean at roughly the same angle as the tower.',
  'Ronald Reagan loved to hula hoop.',
  'Wearing your shoes on the wrong feet makes it easier to walk backwards.',
  'If a deer lives 3400 feet above sea level or higher, it is then referred to as an elk.',
  'The letter K was not added to the english alphabet until 1732.',
  'The first rocking chairs used to only rock forward.'
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
