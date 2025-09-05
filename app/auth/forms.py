from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError
from flask_babel import _, lazy_gettext as _l
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField(_l('Username'),validators=[DataRequired()])
    password = PasswordField(_l('Password'),validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Sign In'))

class UserRegisterForm(FlaskForm):
    username = StringField(_l('username'),validators=[DataRequired()])
    email = StringField(_l('email'),validators=[DataRequired(),Email()])
    password = PasswordField(_l('password'), validators=[DataRequired()])
    password_repeated = PasswordField(
        _l('Repeat password'),validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_name(self,username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError(_('Please use a different username'))
    
    def validate_email(self,email):
        user_email = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user_email is not None:
            raise ValidationError(_('Please use a different email address'))
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

