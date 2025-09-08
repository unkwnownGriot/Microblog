from flask_mail import Message
from flask import current_app
from app import mail
from threading import Thread


def send_async_mail(flask_app,msg):
    with flask_app.app_context():
        try:
         mail.send(msg)
        except Exception as e:
           print(e)


def send_mail(subject,sender,recipients,text_body,html_body):
    msg = Message(subject=subject,sender=sender,
                  recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_mail,
           args=(current_app._get_current_object(), msg)).start()

