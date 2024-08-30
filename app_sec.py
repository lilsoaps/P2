from app_sec import create_app
from flask_session import Session
from datetime import timedelta
from flask import session, request, redirect, url_for
import os

app = create_app()  # create_app() in __init__.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEYSEC')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  


Session(app)

if __name__ == '__main__':
    app.run(debug=True)
