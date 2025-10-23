import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://devuser:sanda3@db:65533/campus_life'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
