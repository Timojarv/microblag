#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Post
from app.forms import EditForm
from pbkdf2 import crypt
from datetime import datetime, timedelta

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(nickname = 'John', email = 'john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_auth(self):
        passwd = 'unit_test_pass'
        u = User(nickname = 'UnitTester', email = 'unit@test.com', pwhash=crypt(passwd))
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(email='nonexistent@test.com').first()
        assert u is None
        u = User.query.filter_by(email='unit@test.com').first()
        assert u is not None
        assert u.pwhash == crypt(passwd, u.pwhash)

    def test_nicknames(self):
        nick = 'John'
        u = User(nickname = nick, email = 'john@example.com', pwhash='notnecessary')
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(nickname=nick).first()
        assert u != None

    def test_follow(self):
        u1 = User(nickname='John', email='john@email.com')
        u2 = User(nickname='Susan', email='susan@email.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().nickname == 'Susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().nickname == 'John'
        u = u1.unfollow(u2)
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        #First we make 4 users:
        u1 = User(nickname='john', email='john@email.com')
        u2 = User(nickname='susan', email='susan@email.com')
        u3 = User(nickname='mary', email='mary@email.com')
        u4 = User(nickname='david', email='david@email.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        #Now we make 4 posts:
        utcnow = datetime.utcnow()
        p1 = Post(body='Post from John', author=u1, timestamp=utcnow +timedelta(seconds=1))
        p2 = Post(body='Post from Susan', author=u2, timestamp=utcnow +timedelta(seconds=2))
        p3 = Post(body='Post from Mary', author=u3, timestamp=utcnow +timedelta(seconds=3))
        p4 = Post(body='Post from David', author=u4, timestamp=utcnow +timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        #Now let's do the 'following'
        u1.follow(u1) #John follows himself
        u1.follow(u2) #John follows Susan
        u1.follow(u4) #John follows David
        u2.follow(u2) #Susan follows herself
        u2.follow(u3) #Susan follows Mary
        u3.follow(u3) #Mary follows herself
        u3.follow(u4) #Mary follows David
        u4.follow(u4) #David follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        #Now we check tha posts
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

if __name__ == '__main__':
    unittest.main()
