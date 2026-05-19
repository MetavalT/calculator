import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///calculator.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False