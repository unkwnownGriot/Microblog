from app.auth import bp
from app.auth.email import send_password_reset_mail
from app.auth.forms import UserRegisterForm,LoginForm,ResetPasswordForm,ResetPasswordRequestForm
from flask import redirect,render_template,url_for,flash,request
from urllib.parse import urlsplit
from app import db
from flask_babel import _
import sqlalchemy as sa
from flask_login import current_user,login_user,logout_user
from app.models import User



# User Login
@bp.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for('auth.login'))
        login_user(user=user,remember=form.remember_me.data)
        #this is in case the user wanted to access a different 
        # route when not authenticated
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html',form=form,title='Sign In',url_for=url_for)

#User logout functions logic
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))



# User registering in the app
@bp.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserRegisterForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(form.username.data == User.username))
        if user is not None:
            flash(_("This user already exist in database"))
            return redirect(url_for('auth.register'))
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password_repeated.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulatiosn you've been registered"))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',title='Register',form=form)


#Reset password functions logic
@bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        print(user)
        if user:
            send_password_reset_mail(user)
        flash(_('Check your emails'))
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html',title='Reset Password',form=form)



@bp.route('/reset_password/<token>', methods=['POST','GET'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.check_token_validity(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
   
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Passsword has been reset'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)