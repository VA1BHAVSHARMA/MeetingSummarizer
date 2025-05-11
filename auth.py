from flask import redirect, session
from google_auth_oauthlib.flow import Flow

def get_google_auth():
    flow = Flow.from_client_secrets_file(
        'meet-client-secret.json',
        scopes=['email', 'profile'],
        redirect_uri='http://localhost:5000/'
    )
    auth_url, state = flow.authorization_url()
    session['state'] = state
    return auth_url