import logging

from models import database
from models.entities import Flight, Note
from web.controllers import app_factory


def create_tables():
    with database:
        database.create_tables([Flight, Note])


if __name__ == '__main__':
    create_tables()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    app = app_factory.make_app()

    app.run(host='127.0.0.1', port='5000', use_reloader=True, debug=True)
