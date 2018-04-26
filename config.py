import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.blogz.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '25'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME','admin@blogz.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','admin@blogz.com')
    BLOGZ_MAIL_SUBJECT_PREFIX = '[BlogZ]'
    BLOGZ_MAIL_SENDER = 'BlogZ Admin <admin@blogz.com>'
    BLOGZ_ADMIN = os.environ.get('BLOGZ_ADMIN','admin@blogz.com')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLOGZ_POSTS_PER_PAGE = 20
    WHOOSH_BASE = os.path.join(basedir, 'search')
    #WHOOSH_DISABLED = True 使能这个就不能进行搜索了
    
    DOC_DIR = os.path.join(basedir, 'app', 'static', 'doc')
    @staticmethod
    def init_app(app):
        pass

#定义使用的数据库路径
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
