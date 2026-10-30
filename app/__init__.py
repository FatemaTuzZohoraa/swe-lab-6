import os

from flasgger import Swagger
from flask import Flask

from .db import init_db
from .events_bus import EventBus
from .notifications import NotifierFactory, make_handler
from .repositories import BookRepository, LoanRepository, MemberRepository
from .routes import bp
from .services import LoanService, ReportService


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DB_PATH=os.environ.get("DB_PATH", "library.db"),
        NOTIFIER=os.environ.get("NOTIFIER", "console"))
    if config:
        app.config.update(config)

    path = app.config["DB_PATH"]
    init_db(path)
    members, books, loans = MemberRepository(path), BookRepository(path), LoanRepository(path)

    bus = EventBus()
    handler = make_handler(NotifierFactory.create(app.config["NOTIFIER"]), members)
    bus.subscribe("book_borrowed", handler)
    bus.subscribe("book_returned", handler)

    app.extensions["svc"] = {
        "members": members, "books": books, "loans": loans,
        "loan": LoanService(members, books, loans, bus),
        "report": ReportService(loans)}
    Swagger(app)  # API docs at /apidocs/
    app.register_blueprint(bp)
    return app
