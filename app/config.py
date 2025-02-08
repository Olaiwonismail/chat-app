import os
# database_url

db = os.getenv('database_url')
sk = os.getenv('secret_key')
class Config:
    SQLALCHEMY_DATABASE_URI = db

    #SQLALCHEMY_DATABASE_URI = 'sqlite:///sql.db'
    SECRET_KEY= sk
    MAIL_SERVER='smtp.gmail.com'


    # MAIL_PORT=587
    # MAIL_USE_TLS=True
    # MAIL_USE_SSL=False
    # MAIL_USERNAME='olaiwonismail@gmail.com'
    # MAIL_PASSWORD='oladayo@14'
