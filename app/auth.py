import os
from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, session, flash

from .database import verify_user, add_user, get_user_password, get_username, check_password,clear_login_attempts,increment_login_attempts,check_login_attempts,update_password,update_avatar
from werkzeug.security import generate_password_hash, check_password_hash
import re
from email_validator import validate_email, EmailNotValidError
# Regex para validação de email mais robusta
regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
auth = Blueprint('auth', __name__)

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)  # Store hashed password
        
        
@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        errors = {}
        
        print(f"Received login request for email: {email}")
        
        can_attempt, error_message = check_login_attempts(email)
        if not can_attempt:
            print(f"Login denied for email: {email} - {error_message}")
            errors["attempts"] = error_message
            return render_template('login.html', email=email, errors=errors)
        
        user_password = get_user_password(email)
        if user_password and check_password_hash(user_password, password):

            session.permanent = True
            session.clear()
            session['user'] = {'email': email, 'username': get_username(email)}
            session.modified = True  
            clear_login_attempts(email)
            print(f"Login successful for email: {email}")
            return redirect(url_for('views.home'))
        else:
            print(f"Invalid login attempt for email: {email}")
            increment_login_attempts(email)
            errors["invalid"] = "Invalid email or password."
            return render_template('login.html', email=email, errors=errors)
    else:
        print("Rendering login page.")
        return render_template('login.html')

@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']
        password_confirm = request.form['password2']
        username = request.form['username']
        errors = {}

        # Validate email
        try:
            valid = validate_email(email)
            email = valid.email  # Update with normalized email
        except EmailNotValidError as e:
            errors["email"] = str(e)
        
        # Stronger password requirements
        if len(password) < 12:
            errors["length"] = "Password must be at least 12 characters long."
        if not re.search(r"[a-z]", password):
            errors["lowercase"] = "Password must contain at least one lowercase letter."
        if not re.search(r"[A-Z]", password):
            errors["uppercase"] = "Password must contain at least one uppercase letter."
        if not re.search(r"[0-9]", password):
            errors["number"] = "Password must contain at least one number."
        if not re.search(r"[@#$%^&+=_!]", password):
            errors["special"] = "Password must contain at least one special character (e.g., @, #, $, etc.)."
        if password != password_confirm:
            errors["confirm"] = "Passwords do not match."

        if not errors:
            if not verify_user(email):
                hashed_password = generate_password_hash(password)
                add_user(email, hashed_password, username)  # Store hashed password
                return redirect(url_for('auth.login'))
            else:
                flash('Email is already in use.', 'error')
                return render_template('sign_up.html', email_in_use=True, email=email, username=username)
        
        return render_template('sign_up.html', errors=errors, email=email, username=username)
    else:
        return render_template('sign_up.html')

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        email = session['user']['email']
        old_password = request.form['old-password']
        new_password = request.form['new-password']
        new_password_confirm = request.form['confirm-password']
        errors = {}
        
        # Validate passwords and other fields
        if not check_password_hash(get_user_password(email), old_password):
            errors['old-password'] = 'Incorrect password.'
        if new_password != new_password_confirm:
            errors['new-password'] = 'Passwords do not match.'
        if len(new_password) < 12:
            errors['length'] = 'Password must be at least 12 characters long.'
        if not re.search(r"[a-z]", new_password):
            errors['lowercase'] = 'Password must contain at least one lowercase letter.'
        if not re.search(r"[A-Z]", new_password):
            errors['uppercase'] = 'Password must contain at least one uppercase letter.'
        if not re.search(r"[0-9]", new_password):
            errors['number'] = 'Password must contain at least one number.'
        if not re.search(r"[@#$%^&+=_!]", new_password):
            errors['special'] = 'Password must contain at least one special character (e.g., @, #, $, etc.).'
            
        if errors:
            return jsonify(errors=errors), 400
        
        new_hashed_password = generate_password_hash(new_password)
        update_password(email, new_hashed_password)
        return jsonify(success=True), 200
    
    return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'))

@auth.route('/change_avatar', methods=['POST'])
def change_avatar():
    email = session['user']['email']
    errors = {}

    # Handle avatar upload
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file:  
            filename = file.filename  
            file.save(os.path.join(current_app.root_path, 'static/uploads/', filename))  
            print(current_app.root_path)

            update_avatar(email, filename)

            # Update session data
            session['user']['avatar'] = filename
            errors["avatar"] = "Avatar updated successfully."
        else:
            errors["avatar"] = "Failed to upload the file."

    # Debug print errors
    print(errors)

    return render_template('profile.html', email=session['user']['email'], username=session['user']['username'], avatar=session['user'].get('avatar'), errors=errors)



