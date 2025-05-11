import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from auth import get_google_auth
from meeting_bot import join_meeting_and_record
from summarize import generate_summary
from database import save_summary, get_user_history
from flask_login import LoginManager, login_user, logout_user, current_user
import datetime
import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summaries.db'
db = SQLAlchemy(app)

# Google OAuth configuration
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv("google_oauth_client_id")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv("google_oauth_client_secret")
google_bp = make_google_blueprint(scope=[
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
])
app.register_blueprint(google_bp, url_prefix='/login')

# Summary Database model 
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(150))
    date = db.Column(db.String(100))
    summary = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    user = session.get('user')
    history = []
    if user:
        history = Summary.query.filter_by(user_email=user['email']).all()
    return render_template('index.html', summary=None, history=history)

@app.route("/login")
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo')
    if resp.ok:
        session['user'] = resp.json()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/join_meeting", methods=["POST"])
# @login_required
def join_meeting():
    # platform = request.form.get("platform")
    meeting_link = request.form.get("meeting_link")
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    transcript = join_meeting_and_record(meeting_link)
    summary = generate_summary(transcript)

    # Save summary to database
    new_summary = Summary(user_email=user['email'], date=str(datetime.date.today()), summary=summary)
    db.session.add(new_summary)
    db.session.commit()

    history = Summary.query.filter_by(user_email=user['email']).all()
    return render_template('index.html', summary=summary, history=history)

    # save_summary(current_user.id, summary)
    # return render_template("index.html", summary=summary)

@app.route("/history")
# @login_required
def history():
    summaries = get_user_history(current_user.id)
    return render_template("history.html", summaries=summaries)

@app.route("/send_email")
# @login_required
def send_email():
    user = session.get('user')
    from summarize import send_email_summary
    send_email_summary(user['email'])
    return "Email Sent!"

if __name__ == "__main__":
    app.run(debug=True)