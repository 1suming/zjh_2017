# -*- coding: utf-8 -*-
__author__ = 'Administrator'

class WebConfig(object):
    """Base config class."""
    pass

class ProdConfig(WebConfig):
    """Production config class."""
    pass

class DevConfig(WebConfig):
    """Development config class."""
    # Open the DEBUG
    DEBUG = True
    HOST='0.0.0.0'
    PORT=8000
    UPLOAD_FOLDER = '/web/static'

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
