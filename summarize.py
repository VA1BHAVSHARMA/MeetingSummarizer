from flask import request, session, redirect,url_for
import smtplib
import http.client
import smtplib
import json
import datetime
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv



def generate_summary(text):
    conn = http.client.HTTPSConnection("api.apyhub.com")

    payload = "{\"text\": \""+text+"\"}"

    headers = {
        'apy-token': os.getenv("account1_apy_token"),
        'Content-Type': "application/json"
        }

    conn.request("POST", "/ai/summarize-text", payload, headers)

    res = conn.getresponse()
    dataStr = res.read().decode("utf-8")

    return (json.loads(dataStr))["data"]["summary"]

def send_email_summary(user_email):
    summary = request.form['summary']
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    sender_email = 'yourmeetingsummarizer@gmail.com'
    receiver_email = user['email']
    password = os.getenv("google_app_password")

    message = MIMEText(summary)
    message['Subject'] = "Meeting Summary ("+ str(datetime.date.today()) + ")"
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print(f'Error sending email: {e}')

    return redirect(url_for('index'))