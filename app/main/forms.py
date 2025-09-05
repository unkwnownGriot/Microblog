from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length,ValidationError
import sqlalchemy as sa
from app import db
from flask import request
from flask_babel import _,lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('username'),validators=[DataRequired()])
    about_me = TextAreaField(_l('Bio'),validators=[Length(min=0,max=200)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self,username):
        if(username.data != self.original_username):
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError(_('please use a different username'))
            

class PostForm(FlaskForm):
    post = TextAreaField(_l('Enter your post'), validators=[DataRequired(),Length(min=1, max=256)])
    submit = SubmitField(_l('Post'))

class FollowUnfollowForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
    query = StringField('Search',validators=[DataRequired()])

    def __init__(self,*args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}

        super(SearchForm,self).__init__(*args, **kwargs)
