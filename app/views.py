from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from .auth import session
from .database import *
from werkzeug.exceptions import BadRequest


views = Blueprint('views', __name__)

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
            flash('A valid Product ID is required.', 'error')
            return redirect(url_for('views.products'))

        product_id = int(product_id)
        product = get_product_by_id(product_id)
        reviews = get_reviews(product_id)

        if 'ratings' in request.form and 'p-review' in request.form:
            email = session.get('user', {}).get('email')
            if not email:
                flash('User must be logged in to add a review.', 'error')
                return redirect(url_for('login'))

            ratings = request.form.get('ratings')
            p_review = request.form.get('p-review')
            if not ratings or not ratings.isdigit():
                flash('A valid rating is required.', 'error')
            elif not p_review or not p_review.strip():
                flash('Review text cannot be empty.', 'error')
            else:
                try:
                    ratings = int(ratings)
                    if ratings < 1 or ratings > 5:
                        flash('Ratings must be between 1 and 5.', 'error')
                    else:
                        add_review(email, ratings, p_review.strip(), product_id)
                        flash('Review added successfully!', 'success')
                except ValueError:
                    flash('Invalid rating value.', 'error')
            reviews = get_reviews(product_id)

        return render_template('product.html', product=product, reviews=reviews)


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
        return render_template('cart.html', user=user, cart=get_cart(user))
    else:
        return redirect(url_for('auth.login'))

@views.route('/checkout', methods=['GET'])
def checkout():
    if 'user' in session:
        return render_template('checkout.html', user=session['user']["username"])
    else:
        return redirect(url_for('auth.login'))

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
        
        try:
            product_id = validate_integer(request.form.get('product_id'), 'Product ID', min_value=1)
            quantity = validate_integer(request.form.get('quantity'), 'Quantity', min_value=1)
        except BadRequest as e:
            flash(str(e))
            return redirect(request.referrer)
        product = get_product(product_id)

        if product and quantity:
            try:
                add_to_cart(quantity, product[6], product[4], user)
                flash('Product added to cart successfully!', 'success')
            except Exception as e:
                flash(f'Error adding product to cart: {e}', 'danger')
        else:
            flash('Invalid input data.', 'danger')
        return redirect(url_for('views.cart'))
    return redirect(url_for('auth.login'))

@views.route("/remove_item", methods=['POST'])
def remove_item():
    if 'user' in session:
        user = session['user']['username']
        product_id = request.form.get('product_id')
        if product_id:
            remove_from_cart(user, product_id)
            product = get_product_by_id(product_id)
            if product:
                add_quantity(product[4], request.form.get('quantity', 1))
            flash('Item removed from cart successfully!', 'success')
        else:
            flash('Error: Product ID not found.', 'danger')
        return redirect(url_for('views.cart'))
    else:
        return redirect(url_for('auth.login'))

@views.route("/pay", methods=['POST'])
def pay():
    if 'user' in session:
        user = session['user']['username']
        pay_cart(user)
        return redirect(url_for('views.home'))
    return redirect(url_for('auth.login'))
