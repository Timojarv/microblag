from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, RegisterForm, PostForm
from .models import User, Post
from datetime import datetime
from pbkdf2 import crypt
from config import POSTS_PER_PAGE

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    if g.user.is_authenticated():
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
            db.session.add(post)
            db.session.commit()
            flash('msg_type_success')
            flash('Your post is now live!')
            return redirect(url_for('index'))
        user = g.user
        posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, True)
        return render_template('index.html', title='Home', user=user, posts=posts, form=form, extra_css=['modern', 'whitebg'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or user.pwhash != crypt(form.passwd.data, user.pwhash):
            flash('msg_type_warning')
            flash('Invalid credentials!')
            return redirect(url_for('login'))
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        u = user.follow(user)
        if u:
            db.session.add(u)
            db.session.commit()
        login_user(user, remember=remember_me)
        flash('msg_type_success')
        flash('Succesfully logged in!')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html',
                           form=form,
                           extra_css=['login', 'modern'])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user != None:
            form.nickname.errors.append('Nickname already in use.')
            return redirect(url_for('signup'))
        user = User.query.filter_by(email=form.email.data).first()
        if user != None:
            form.email.errors.append('Email already in use.')
            return redirect(url_for_('signup'))
        nickname = form.nickname.data
        user = User(nickname = nickname, email = form.email.data, pwhash=crypt(form.passwd.data))
        db.session.add(user)
        db.session.commit()
        u = user.follow(user)
        if u:
            db.session.add(u)
            db.session.commit()
        flash('msg_type_success')
        flash('Registration succesful!')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html',
                           title='Sign Up',
                           form=form)
'''
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('msg_type_warning')
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    flash('msg_type_success')
    flash('Succesfully logged in!')
    return redirect(request.args.get('next') or url_for('index'))
'''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('msg_type_info')
    flash('Logged out.')
    return redirect(url_for('login'))


@app.route('/u/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('msg_type_warning')
        flash('User %s not found!' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, True)
    return render_template('user.html', user=user, posts=posts, title=user.nickname, extra_css=['whitebg'])


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('msg_type_info')
        flash('Your changes have been saved!')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form, title='Edit profile', extra_css=['modern','whitebg'])

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('msg_type_warning')
        flash("Sorry, but you can't follow a user that doesn't exist.")
        return redirect(url_for('index'))
    if user == g.user:
        flash('msg_type_info')
        flash('Did you really try to follow yourself?')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('msg_type_info')
        flash('You are already following %s.' % nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('msg_type_success')
    flash('You are now following %s!' % nickname)
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('msg_type_warning')
        flash("Sorry, but you can't unfollow a user that doesn't exist.")
        return redirect(url_for('index'))
    if user == g.user:
        flash('msg_type_info')
        flash('Did you really try to unfollow yourself?')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('msg_type_warning')
        flash('You can\'t unfollow a user you are not following %s!' % nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('msg_type_success')
    flash('You have stopped following %s!' % nickname)
    return redirect(url_for('user', nickname=nickname))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', extra_css=['error'], title="404"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', extra_css=['error'], title="500"), 500
