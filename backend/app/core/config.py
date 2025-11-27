import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_USER=os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD=os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST=os.environ.get("DATABASE_HOST")
    DATABASE_NAME=os.environ.get("DATABASE_NAME")
