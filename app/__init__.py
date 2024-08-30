from flask import Flask
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
def create_app():
    app = Flask(__name__)
    csrf.init_app(app)
    # Import blueprints
    from .views import views
    from .auth  import auth
    from .database import setup_database, insert_products,clear_database
    
    clear_database()
    setup_database()
    insert_products()
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth,  url_prefix='/')

    return app