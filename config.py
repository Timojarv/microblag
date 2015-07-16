import os
import hashlib
import binascii
from Crypto.Cipher import AES
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'WcD^cVNxYtjL2YvasJCE7rUEN?PHE&263LTs4u?Msb6Qnp_Y57H6*=C--4YcVUHu'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
#Doin' the magicks
crypted = binascii.unhexlify(os.environ.get('MAIL_PASSWORD'))
obj = AES.new(hashlib.md5('Hello there!'.encode('utf-8')).hexdigest())
MAIL_PASSWORD = obj.decrypt(crypted)[:15].decode('utf-8') #Boom we've got the mail password securely
ADMINS = ['timo.jaerv@gmail.com']

#Pagination
POSTS_PER_PAGE = 16
