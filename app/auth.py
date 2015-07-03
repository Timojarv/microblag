from .models import User
from pbkdf2 import crypt

def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user is None or user.pwhash != crypt(password, user.pwhash):
        return False
    User.follow_self(user)
    return user
