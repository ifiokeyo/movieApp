import os
import logging

import redis

from flask_migrate import Migrate
from flask import Flask, jsonify, render_template
from flask_cors import CORS


try:
    from ..config import app_configuration
    from .api.movies import get_movies
except (ModuleNotFoundError, ImportError):
    from src.config import app_configuration
    from src.app.api.movies import get_movies

redis_db = redis.from_url(os.environ.get('REDIS_URL'))


migrate = Migrate()


def create_flask_app(environment=os.environ.get('FLASK_ENV')):
    # initialize logging module
    log_format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    # initialize Flask
    app = Flask(
        __name__, instance_relative_config=True, static_folder=None
    )

    # to allow cross origin resource sharing
    CORS(app)
    app.config.from_object(app_configuration[environment])
    app.config.from_pyfile('config.py')

    # initialize SQLAlchemy
    try:
        from .models.models import db

    except ModuleNotFoundError:
        from src.app.models.models import db

    db.init_app(app)
    migrate.init_app(app, db)

    app.url_map.strict_slashes = False

    # tests route
    @app.route('/')
    def index():
        return "Welcome to Sender movie listing platform"

    @app.route('/movies', methods=['GET'])
    def get():
        response = get_movies()

        return render_template('movies.html', movies=response)

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(status=500, error='Internal server error',
                                message="""It is not you. It is me. The server encountered an 
                                internal error and was unable to complete your request.  
                                Either the server is overloaded or there is an error in the
                                application"""))
        response.status_code = 500
        return response

    return app

