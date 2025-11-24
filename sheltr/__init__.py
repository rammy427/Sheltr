import os

from flask import (Flask, g, redirect, render_template, url_for)
from flask_bootstrap import Bootstrap5

def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)

    # Generate secure random secret key if not provided
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        secret_key = os.urandom(32).hex()
        print("WARNING: Using randomly generated SECRET_KEY. Set SECRET_KEY environment variable for production.")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=os.path.join(app.instance_path, 'sheltr.sqlite'),
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=86400,
    )
    # Initialize Bootstrap.
    bootstrap = Bootstrap5(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # Redirect to login if not authenticated, otherwise show home
    @app.route('/')
    def index():
        if not hasattr(g, 'user') or g.user is None:
            return redirect(url_for('auth.login'))
        return render_template('index.html')

    from . import donations
    app.register_blueprint(donations.bp)

    from . import emergency
    app.register_blueprint(emergency.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    return app
