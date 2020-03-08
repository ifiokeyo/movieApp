from os import path, environ


class Config(object):
    BASE_DIR = path.dirname(__file__)
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfiguration(Config):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfiguration(Config):
    TESTING = True
    DEBUG = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@db/test_sennder"


app_configuration = {
    'production': Config,
    'development': DevelopmentConfiguration,
    'testing': TestingConfiguration
}
