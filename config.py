from dotenv import load_dotenv
import os

load_dotenv()


class Config(object):
    """Set enviroment Variables"""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PATH = os.getenv("UPLOAD_PATH")
