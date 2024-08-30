from app import create_app
from flask_session import Session
from datetime import timedelta
import os


app = create_app()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30)
app.config['SESSION_COOKIE_NAME'] = 'session2'

Session(app)

if __name__ == "__main__":
    app.run(debug=True)