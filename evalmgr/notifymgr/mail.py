import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from studentmgr.models import Submission


def send_mail(submission_id):
    sub = Submission.objects.get(id=submission_id)
    team = sub.team
    message = MIMEMultipart("alternative")
    message["Subject"] = "Big Data Assignment Result"
    message["From"] = "noreplybigdata@gmail.com"

    html = "Hi \n Your submission for " + sub.evaluation.name + " with submission id " + str(submission_id) + " has been evaluated \n" \
        "<html> " \
        "<body> " \
        "<h3> Scores </h3> " \
        "<p> Marks: " + str(sub.marks) + "</p>" \
        "<h3> Remarks </h3> " + str(sub.message) + "<br>" \
        "</body> "  \
        "</html>"

    part = MIMEText(html, "html")

    message.attach(part)

    emails = [team.email_member_1, team.email_member_2, team.email_member_3, team.email_member_4]
    for email in emails:
        if email != 'nan':
            _send(email, message)


def _send(receiver_email, message):
    print(" Sending mail ")
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreplybigdata@gmail.com"  # Enter your address
    password = "bigdata2019"  # Enter correct password

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())