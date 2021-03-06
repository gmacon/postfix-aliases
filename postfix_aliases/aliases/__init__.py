from flask import Blueprint, flash, redirect, render_template, request, url_for
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


@bp.route('/', methods=['GET', 'POST'])
@login_required
def aliases():
    form = create_new_alias_form()
    if request.method == 'POST':
        if form.validate():
            domain = Domain.query.get(int(form.domain.data))

            alias = Alias(localpart=form.localpart.data,
                          domain=domain,
                          mailbox=current_user)

            db.session.add(alias)
            db.session.commit()
            flash('Added alias {}'.format(alias), 'info')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash('{}: {}'.format(field, error), 'error')

    return render_template('aliases.html', new_alias_form=form)


@bp.route('/<int:alias_id>/delete', methods=['POST'])
@login_required
def delete_alias(alias_id):
    alias = Alias.query.get_or_404(alias_id)
    str_alias = str(alias)
    db.session.delete(alias)
    db.session.commit()
    flash('Deleted alias {}'.format(str_alias), 'info')
    return redirect(url_for('.aliases'))
