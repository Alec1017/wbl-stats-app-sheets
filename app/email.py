from smtplib import SMTP

from app import email_address, email_password, spreadsheet_id


def send_email(name, subject, to_email):
  try:
    server = SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(email_address, email_password)

    message = """Subject: {}\n\n
    Hey {}!

    Here is the link to the updated stat sheet.

    https://docs.google.com/spreadsheets/d/{}/

    sincerely,
    Cookie
    """.format(subject, name, spreadsheet_id)

    server.sendmail(email_address, to_email, message)
    server.quit()
  except Exception as e:
    print("something went wrong, email not sent")
    print(str(e))
    
  
