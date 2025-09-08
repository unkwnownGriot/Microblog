from app.main import bp
from flask import redirect,render_template,request,flash,url_for,current_app,g
from flask_login import login_required,current_user
from app.main.forms import PostForm,EditProfileForm,FollowUnfollowForm,SearchForm
import sqlalchemy as sa
from langdetect import detect,LangDetectException
from app import db
from datetime import datetime, timezone
from flask_babel import _,get_locale
from app.models import Post,User



@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.searchform = SearchForm()
    g.locale = str(get_locale)


@bp.route('/',methods=['GET','POST'])
@bp.route('/index',methods=['GET','POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException :
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    lang_post=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Success'))
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,int)
    posts = db.paginate(current_user.following_posts(),page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],error_out=False)
    next_url = url_for('main.index',page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page = posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',current_user=current_user,
                           posts=posts.items,url_for=url_for,form=form, 
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = FollowUnfollowForm()
    page = request.args.get('page',1,int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query,page=page,per_page=current_app.config['POSTS_PER_PAGE'],error_out=False)
    next_url = url_for('main.user',username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user',username=username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html',user=user,posts=posts.items,
                           next_url=next_url,prev_url=prev_url,form=form)


@bp.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved"))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form,title='Edit profile')

@bp.route('/explore',methods=['GET'])
@login_required
def explore():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    page = request.args.get('page',1,int)
    posts = db.paginate(query,page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.explore',page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html',title='Explore',posts=posts.items, 
                           next_url=next_url, prev_url=prev_url)


@bp.route('/search')
@login_required
def search():
    if not g.searchform.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page',1,int)
    posts, total = Post.search(g.searchform.query.data,page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search',query=g.searchform.query.data,page= page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None 
    prev_url = url_for('main.search', query=g.searchform.query.data,page=page-1) \
        if page > 1 else None
    return render_template('search.html',posts=posts,
                           next_url=next_url,prev_url=prev_url)

@bp.route('/follow/<username>', methods=['POST','GET'])
@login_required
def follow(username):
    form = FollowUnfollowForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(username == User.username))
        if user is None:
            flash(_('User %(username)s not found',username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('you cannot follow yourself'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('now you are following user - %(username)s',username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>',methods=['GET','POST'])
@login_required
def unfollow(username):
    form = FollowUnfollowForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(username==User.username))
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself'))
            return redirect(url_for('main.user',username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You have successfully unfollowed %(username)s', username=username))
        return redirect(url_for('main.user',username=username))
    else:
        return redirect(url_for('main.index'))
    








