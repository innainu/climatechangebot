import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    FB_API_VERSION = 2.6
    FB_ACCESS_TOKEN = 'this-is-in-local-config'
    FB_VERIFY_TOKEN = 'this-is-in-local-config'
    FB_WEBHOOK_URL = 'this-is-in-local-config'
    NYT_KEY = 'this-is-in-local-config'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    # ngrok http -host-header=rewrite 192.168.33.11:80
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
