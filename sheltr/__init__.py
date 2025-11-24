import os

from flask import (Flask, g, redirect, render_template, url_for)
from flask_bootstrap import Bootstrap5

def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # !! TEMPORARY - REMOVE for final version !!
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sheltr.sqlite'),
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

    return app
    from . import donations
    app.register_blueprint(donations.bp)
    
    from . import emergency
    app.register_blueprint(emergency.bp)
    
    return app
