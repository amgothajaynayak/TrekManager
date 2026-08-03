import os

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trek-manager-secret-key-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'trekmanager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
