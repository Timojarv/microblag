from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from app.models import User

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    passwd = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    passwd = PasswordField('password', validators=[DataRequired()])


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False

        if len(self.about_me.data) > 140:
            self.about_me.errors.append('Too many characters!')
            return False

        if self.nickname.data == self.original_nickname:
            return True

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('Sorry, but that nickname was already in use.')
            return False

        return True
