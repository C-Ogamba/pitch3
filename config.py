import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """
    Common configurations
    """
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(basedir), 'app.db')
    SQLACHEMY_TRACK_MODIFICATIONS = False

    #Pagination
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE') or 10)