import logging.config

from flask import Flask

from web.controllers.processor import processing_api


def make_app():
    # Initialize flask application
    logging.debug("Initializing Flask application...")
    app = Flask(__name__)

    logging.debug("Configuring Flask...")
    app.config["ENV"] = 'development'
    app.config["DEBUG"] = True

    # Register blueprints
    logging.debug("Registering Flask blueprints...")
    app.register_blueprint(processing_api)

    return app
