import os

class Config:
    SECTET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
    DEBUG = True