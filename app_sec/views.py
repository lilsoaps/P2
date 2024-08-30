from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from .auth import session
from .database import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
import re


views = Blueprint('views', __name__)


ALLOWED_CHARACTERS = re.compile(r'^[\w\s.,!?@#&*()-_=+;:\'"\u00A0-\uFFFF]+$')

def validate_integer(value, field_name, min_value=None, max_value=None):
    try:
        value = int(value)
        if min_value is not None and value < min_value:
            raise ValueError(f"{field_name} must be at least {min_value}.")
        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} must be at most {max_value}.")
        return value
    except ValueError as e:
        raise BadRequest(str(e))

@views.route('/', methods=['GET', 'POST'])
def home():
    if 'user' in session:
        username = session['user']['username']
        return render_template('index.html', username=username)
    else:
        return redirect(url_for('auth.login'))

@views.route('/product', methods=['GET', 'POST'])
def product_detail():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        product_id = request.args.get('value')
        if not product_id or not product_id.isdigit():
            flash('A valid Product ID is required.', 'error')
            return redirect(url_for('home'))

        product_id = int(product_id)
        product = get_product_by_id(product_id)
        reviews = get_reviews(product_id)

        if not product:
            flash('Product not found.', 'error')
            return redirect(url_for('home'))

        return render_template('product.html', product=product, reviews=reviews)

    elif request.method == 'POST':
        product_id = request.form.get('product_id')
        if not product_id or not product_id.isdigit():
            return redirect(url_for('views.products'))
        

        product_id = int(product_id)
        product = get_product_by_id(product_id)
        reviews = get_reviews(product_id)
        errors = {}
        if 'ratings' in request.form and 'p-review' in request.form:
            email = session.get('user', {}).get('email')
            if not email:
                return redirect(url_for('login'))

            ratings = request.form.get('ratings')
            p_review = request.form.get('p-review')

            if not ratings or not ratings.isdigit():
                errors['ratings'] = 'Ratings is required.'
            elif not p_review or not p_review.strip():
                errors['p-review'] = 'Review is required and cannot be empty.'
            elif len(p_review) > 300:
                errors['p-reviewsize'] = 'Review must be at most 300 characters.'
            elif not ALLOWED_CHARACTERS.match(p_review):
                errors['p-reviewchars'] = 'Review contains invalid characters.'
            else:
                try:
                    ratings = int(ratings)
                    if ratings < 1 or ratings > 5:
                        errors['ratings'] = 'Ratings must be between 1 and 5.'
                    else:
                        add_review(email, ratings, p_review.strip(), product_id)
                except ValueError:
                    errors['ratings'] = 'Ratings must be a number.'
            reviews = get_reviews(product_id)

        return render_template('product.html', product=product, reviews=reviews, errors=errors)


@views.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        email = session['user']['email']
        return render_template('about.html', session_user=email)
    else:
        if 'user' in session:
            email = session['user']['email']
            return render_template('about.html', session_user=email)
        else:
            return redirect(url_for('auth.login'))

@views.route('/cart', methods=['GET'])
def cart():
    if 'user' in session:
        user = session['user']['username']
        total_price = get_total_price(user)
        return render_template('cart.html', user=user, cart=get_cart(user), total_price=total_price)
    else:
        return redirect(url_for('auth.login'))

@views.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        

    errors = {}
    
    if cart_is_empty(session['user']['username']):
        errors['cart'] = 'Your cart is empty. Please add items to your cart before proceeding to checkout.'
        return render_template('cart.html', user=session['user']["username"], errors=errors)

    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        ccard = request.form.get('ccard')
        exp = request.form.get('exp')
        cvcv = request.form.get('cvcv')
        password = request.form.get('password')
        

        if not fname:
            errors['fname'] = 'First name is required.'
        if not lname:
            errors['lname'] = 'Last name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not ccard:
            errors['ccard'] = 'Credit card number is required.'
        if not exp:
            errors['exp'] = 'Expiration date is required.'
        if not cvcv:
            errors['cvcv'] = 'CVCV is required.'
        if not password:
            errors['password'] = 'Password is required.'
        else:
            stored_password = get_user_password(email)
            if not (stored_password and check_password_hash(stored_password, password)):
                errors['password'] = 'Invalid password. Please re-enter your password.'

        if errors:
            return render_template('checkout.html', user=session['user']["username"], errors=errors)

        return redirect(url_for('views.home'))

    return render_template('checkout.html', user=session['user']["username"], errors=errors)



@views.route("/products", methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        query = request.form['query'].upper().split(" ")
        lista_produtos = get_specific_products(query)
        return render_template('products.html', lista=lista_produtos, user=session['user']["username"])
    else:
        if 'user' in session:
            return render_template('products.html', lista=get_products(), user=session['user']["username"])
        else:
            return redirect(url_for('auth.login'))
        

@views.route("/add_cart", methods=['POST'])
def add_cart():
    if 'user' in session:
        user = session['user']['username']
        errors = {}        
        try:
            product_id = validate_integer(request.form.get('product_id'), 'Product ID', min_value=1)
            quantity = validate_integer(request.form.get('quantity'), 'Quantity', min_value=1)
        except BadRequest as e:
            errors['error'] = str(e)
            return redirect(request.referrer)
        
        product = get_product(product_id)
        
        if product:
            available_quantity = product[1]  
            if available_quantity >= quantity:
                try:

                    add_to_cart(quantity, product[6], product[4], user)  
                
                    remove_quantity(product[4], quantity)
                    
                    errors['success'] = 'Product added to cart successfully!'
                except Exception as e:
                    errors['error'] = str(e)
            else:
                errors['error'] = 'The desired quantity is not available.'
        else:
            errors['error'] = 'Product not found.'
        
        return redirect(url_for('views.cart'))
    else:
        return redirect(url_for('auth.login'))

@views.route("/remove_item", methods=['POST'])
def remove_item():
    errors = {}
    if 'user' in session:
        user = session['user']['username']
        product_id = request.form.get('product_id')
        if product_id:
            remove_from_cart(user, product_id)
            product = get_product_by_id(product_id)
            if product:
                add_quantity(product[4], request.form.get('quantity', 1))
            errors['success'] = 'Product removed from cart successfully!'
        else:
            errors['error'] = 'Product not found.'
        return redirect(url_for('views.cart'))
    else:
        return redirect(url_for('auth.login'))

@views.route("/pay", methods=['POST'])
def pay():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']['username']
    email = session['user']['email']
    password = request.form.get('password')
    errors = {}


    if not password:
        errors['password'] = 'Password is required.'
        return render_template('checkout.html', user=user, errors=errors)


    stored_password = get_user_password(email)
    if not (stored_password and check_password_hash(stored_password, password)):
        errors['password'] = 'Invalid password. Please re-enter your password.'
        return render_template('checkout.html', user=user, errors=errors)


    try:
        pay_cart(user)
    except Exception as e:
        errors['payment'] = f"Payment failed: {str(e)}"
        return render_template('checkout.html', user=user, errors=errors)


    return redirect(url_for('views.home'))
