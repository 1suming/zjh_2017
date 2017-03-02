# -*- coding: utf-8 -*-
__author__ = 'Administrator'

class Config(object):
    """Base config class."""
    pass

class ProdConfig(Config):
    """Production config class."""
    pass

class DevConfig(Config):
    """Development config class."""
    # Open the DEBUG
    DEBUG = True
    HOST='0.0.0.0'
    PORT=8000
    UPLOAD_FOLDER = 'static/upload'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
