import click
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
import yaml

from . import aliases, user
from .models import db, Domain, Mailbox
from .password import hash_ssha512


app = Flask(__name__)
app.config.from_envvar('POSTFIX_ALIASES_SETTINGS')

login_manager = LoginManager(app)
login_manager.login_view = 'user.login'

db.init_app(app)

csrf = CsrfProtect(app)


@login_manager.user_loader
def load_user(user_id):
    return Mailbox.query.get(int(user_id))


app.register_blueprint(aliases.bp, base_url='/')
app.register_blueprint(user.bp, base_url='/user')


@app.cli.command()
def initdb():
    db.create_all()


@app.cli.command()
@click.argument('domain')
def create_domain(domain):
    Domain.new(domain)
    db.session.commit()


@app.cli.command()
@click.password_option()
@click.argument('email')
def create_mailbox(password, email):
    user = Mailbox.new(email)
    if password:
        user.password = hash_ssha512(password)
    db.session.commit()


@app.cli.command()
@click.argument('mailbox')
@click.argument('alias')
def add_alias(mailbox, alias):
    mailbox_obj = Mailbox.get(mailbox)
    mailbox_obj.add_alias(alias)
    db.session.commit()


@app.cli.command()
@click.password_option()
@click.argument('email')
def reset_password(password, email):
    mailbox = Mailbox.get(email)
    mailbox.password = hash_ssha512(password)
    db.session.commit()


@app.cli.command()
@click.argument('alias_yaml', type=click.File('r'))
def load_data(alias_yaml):
    data = yaml.safe_load(alias_yaml)

    for mailbox_addr, mailbox_info in data.items():
        mailbox = Mailbox.ensure(mailbox_addr)
        mailbox.password = mailbox_info.get('passwd')

        aliases = mailbox_info.get('aliases', ())
        for alias in aliases:
            mailbox.add_alias(alias)

    db.session.commit()


@app.cli.command()
@click.argument('alias_yaml', type=click.File('w'))
def dump_data(alias_yaml):
    data = {}
    for mailbox in Mailbox.query:
        mailbox_info = {
            'passwd': mailbox.password,
            'aliases': [str(a) for a in mailbox.aliases],
        }
        data[str(mailbox)] = mailbox_info
    yaml.safe_dump(data, alias_yaml)
