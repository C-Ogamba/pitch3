from mailbox import NotEmptyError
from app import app, db
from flask import render_template, url_for, redirect, request, flash
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PitchForm
from app.models import User,Pitch
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pitches = Pitch.query.order_by(Pitch.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=pitches.next_num) \
        if pitches.has_next else None
    prev_url = url_for('index', page=pitches.prev_num) \
        if pitches.has_prev else None
    form = PitchForm()
    if form.validate_on_submit():
        pitch = Pitch(body=form.body.data, author=current_user)
        db.session.add(pitch)
        db.session.commit()
        flash('Your pitch has been added!', 'success')
        return redirect(url_for('index'))
    return render_template(
        'index.html',
        title='Home',
        form=form,
        pitches=pitches.items,
        next_url=next_url,
        prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('You are now logged in!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pitches = user.pitches.order_by(Pitch.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('profile', username=user.username, page=pitches.next_num) \
        if pitches.has_next else None
    prev_url = url_for('profile', username=user.username, page=pitches.prev_num) \
        if pitches.has_prev else None
    return render_template(
        'profile.html',
        title='User Profile',
        username=username,
        user=user,
        next_url=next_url,
        prev_url=prev_url,
        pitches=pitches.items)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template(
        'edit_profile.html',
        title='Edit Profile',
        form=form)