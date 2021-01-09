from decouple import config


class Config(object):
    """
    This clas is containing secretkey and databse url of postgres
    """
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL')
