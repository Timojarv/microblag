from flask.ext.mail import Message
from flask import render_template
from app import mail
from config import ADMINS
from threading import Thread
from app import app
from .decorators import async
import uuid

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def follower_notification(followed, follower):
    send_email('[MicroBlag] %s is now following you!' % follower.nickname,
    ADMINS[0],
    [followed.email],
    render_template('follower_email.txt', user=followed, follower=follower),
    render_template('follower_email.html', user=followed, follower=follower, token=uuid.uuid4()))
