import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trek-management-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trek.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
