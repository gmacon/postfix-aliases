from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

from ..models import Domain, Mailbox
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
