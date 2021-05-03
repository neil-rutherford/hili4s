from flask import render_template, redirect, url_for, flash, request
from app.auth import bp
from app.models import User, Region
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import RegisterForm, LoginForm
import datetime
from werkzeug.urls import url_parse

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    regions = Region.query.all()
    region_list = [(i.id, i.name) for i in regions]
    form = RegisterForm()
    form.region_id.choices = region_list
    if form.validate_on_submit():
        user = User()
        user.region_id = int(form.region_id.data)
        user.stripe_customer_id = str(form.stripe_customer_id.data)
        user.email = str(form.email.data)
        user.password_hash = user.set_password(str(form.password.data))
        user.first_name = str(form.first_name.data)
        user.last_name = str(form.last_name.data)
        user.user_type = int(form.user_type.data)
        user.comments = str(form.comments.data)
        user.is_blacklist = False
        user.is_drug = False
        user.is_background = False
        user.last_active = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash("Welcome, {}!".format(user.first_name))
        return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data)).first()
        if user is None or not user.check_password(str(form.password.data)):
            flash('Invalid email or password.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        flash("Welcome, {}!".format(user.first_name))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('auth/login.html', title='Log In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('main.index'))