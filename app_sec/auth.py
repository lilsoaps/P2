import base64
from io import BytesIO
from flask import Blueprint, app, jsonify, render_template, request, redirect, url_for, session
from flask import current_app, session, request, jsonify
import qrcode
from .database import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
from email_validator import validate_email, EmailNotValidError
import hashlib
import requests
import pyotp
import time
import os

auth = Blueprint('auth', __name__)

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)  

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        
def check_breached_password(password):
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError("Error fetching breached passwords")

    hash_suffixes = (line.split(':') for line in response.text.splitlines())
    for hsuffix, count in hash_suffixes:
        if suffix == hsuffix:
            return True
    return False

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        totp_code = request.form['totp'].strip()
        errors = {}
        
        can_attempt, error_message = check_login_attempts(email)
        if not can_attempt:
            errors["attempts"] = error_message
            return render_template('login.html', email=email, errors=errors)

        user_password = get_user_password(email)

        if user_password and check_password_hash(user_password, password):
            user_totp_secret = get_user_totp_secret(email)
            
            totp = pyotp.TOTP(user_totp_secret)

            is_totp_valid = totp.verify(totp_code, valid_window=3)
            
            if check_breached_password(password):
                errors["breached"] = "This password has been compromised in a data breach. Please choose a different password."
                return render_template('login.html', email=email, errors=errors)

            if is_totp_valid:
                session.permanent = True
                session.clear()
                session['user'] = {'email': email, 'username': get_username(email)}
                clear_login_attempts(email)

                return redirect(url_for('views.home'))
            else:
                errors["incorrect_totp"] = "Invalid TOTP code."
                increment_login_attempts(email)
                return render_template('login.html', email=email, errors=errors)
        else:
            errors["incorrect_password"] = "Invalid email or password."
            increment_login_attempts(email)
            return render_template('login.html', email=email, errors=errors)
    return render_template('login.html')



@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']
        password_confirm = request.form['password2']
        username = request.form['username']
        errors = {}
        
        if email_exists(email):
            errors["email"] = "Email already exists. Please choose a different email."

        if username_exists(username):
            errors["username"] = "Username already exists. Please choose a different username."

        password = re.sub(r'\s+', ' ', password).strip()
        password_confirm = re.sub(r'\s+', ' ', password_confirm).strip()


        if check_breached_password(password):
            errors["breached"] = "This password has been compromised in a data breach. Please choose a different password."

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            errors["email"] = str(e)

        if len(password) < 12 or len(password) > 128:
            errors["length"] = "Password must be at least 12 characters long and less than 128 characters."
        if password != password_confirm:
            errors["confirm"] = "Passwords do not match."

        if not errors:
            if not verify_user(email):

                totp_secret = pyotp.random_base32()
                
                add_user(email, generate_password_hash(password), username, totp_secret)

                totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=email, issuer_name="eDeti shop")
                qr = qrcode.make(totp_uri)
                img_io = BytesIO()
                qr.save(img_io, 'PNG')
                img_io.seek(0)
                qr_data = img_io.getvalue()
                qr_b64 = base64.b64encode(qr_data).decode('ascii')
                qr_image = f"data:image/png;base64,{qr_b64}"

                return render_template('sign_up.html', totp_uri=totp_uri, totp_qr_image=qr_image)

            else:
                return render_template('sign_up.html', email_in_use=True, email=email, username=username)
        
        return render_template('sign_up.html', errors=errors, email=email, username=username)
    
    return render_template('sign_up.html')

@auth.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('auth.login'))


@auth.route('/change_avatar', methods=['POST'])
def change_avatar():
    email = session['user']['email']
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    errors = {}
    MAX_FILE_SIZE = 5*1024*1024

    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            if file.tell() > MAX_FILE_SIZE:
                errors["avatar"] = "File size exceeds 5MB."
                return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'), errors=errors)
            
            file.seek(0)
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.root_path, 'static/uploads', filename))

            update_avatar(email, filename)

            session['user']['avatar'] = filename
            errors["avatar"] = "Avatar updated successfully."
        else:
            errors["avatar"] = "Invalid file type. Please upload a valid image file."

    if errors:
        return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'), errors=errors)

    return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'))



@auth.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        email = session['user']['email']
        errors = {}

        # Handle password change
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        new_password_confirm = request.form.get('confirm-password')

        new_password = re.sub(r'\s+', ' ', new_password).strip()
        new_password_confirm = re.sub(r'\s+', ' ', new_password_confirm).strip()

        if not check_password_hash(get_user_password(email), old_password):
            errors['old-password'] = 'Incorrect password.'

        if check_breached_password(new_password):
            errors['breached'] = "This password has been compromised in a data breach. Please choose a different password."

        if new_password != new_password_confirm:
            errors['new-password'] = 'Passwords do not match.'
        if len(new_password) < 12 or len(new_password) > 128:
            errors['length'] = 'Password must be at least 12 characters long and less than 128 characters.'

        if errors:
            return jsonify(errors=errors), 400

        new_hashed_password = generate_password_hash(new_password)
        update_password(email, new_hashed_password)
        return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'), password_updated=True)

    return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'))

@auth.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    email = session['user']['email']
    
    delete_user_account(email)
    
    session.clear()
    return redirect(url_for('auth.login'))



