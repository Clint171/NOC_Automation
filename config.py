import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://flask_user:securepassword@localhost/network_monitoring"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
