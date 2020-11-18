import os

from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    UPLOAD_FOLDER = os.path.join(basedir, "data")
    IMAGES_FOLDER = "images"
    # IMAGES_FOLDER = os.path.join(basedir, "images")
