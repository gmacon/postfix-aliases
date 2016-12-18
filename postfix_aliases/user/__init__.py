from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import db, Mailbox
from ..password import hash_ssha512, check_ssha512


bp = Blueprint('user', __name__, template_folder='templates')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        mailbox = Mailbox.get(form.email.data)
        if mailbox:
            if check_ssha512(form.password.data, mailbox.password):
                login_user(mailbox)
                return redirect('/')
    return render_template('login.html', form=form)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(),
                                             EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired()])


@bp.route('/changepassword', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_ssha512(form.old_password.data, current_user.password):
            current_user.password = hash_ssha512(form.new_password.data)
            db.session.commit()
            flash('Password change successful')
            return redirect('/')
    return render_template('pwchange.html', form=form)
