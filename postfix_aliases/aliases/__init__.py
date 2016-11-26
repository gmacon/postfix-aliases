from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

from ..models import db, Domain, Alias


bp = Blueprint('aliases', __name__, template_folder='templates')


class NewAliasForm(FlaskForm):
    localpart = StringField(validators=[DataRequired()])
    domain = SelectField(validators=[DataRequired()])


def create_new_alias_form():
    form = NewAliasForm()
    form.domain.choices = [(str(d.id), d.name) for d in Domain.query]
    form.domain.choices.insert(0, ('', 'Choose a domain...'))
    return form


@bp.route('/')
@login_required
def aliases():
    new_alias_form = create_new_alias_form()
    return render_template('aliases.html',
                           new_alias_form=new_alias_form)


@bp.route('/new', methods=['POST'])
@login_required
def new_alias():
    form = create_new_alias_form()
    if form.validate_on_submit():
        domain = Domain.query.get(int(form.domain.data))

        alias = Alias(localpart=form.localpart.data,
                      domain=domain,
                      mailbox=current_user)

        db.session.add(alias)
        db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash('{}: {}'.format(field, error), 'error')

    return redirect(url_for('.aliases'))
