import click
from flask import Flask
from flask_login import LoginManager
import yaml

from . import aliases, user
from .models import db, Alias, Domain, Mailbox
from .password import hash_ssha512


app = Flask(__name__)
app.config.from_envvar('POSTFIX_ALIASES_SETTINGS')

login_manager = LoginManager(app)
login_manager.login_view = 'user.login'

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Mailbox.query.get(int(user_id))


app.register_blueprint(aliases.bp, base_url='/')
app.register_blueprint(user.bp, base_url='/user')


@app.cli.command()
def initdb():
    db.create_all()


@app.cli.command()
@click.password_option()
@click.argument('email')
def create_mailbox(password, email):
    localpart, at, domain = email.partition('@')

    domain_obj = Domain.query.filter(Domain.name == domain.lower()).first()
    if not domain_obj:
        domain_obj = Domain(name=domain.lower())
        db.session.add(domain_obj)

    mailbox = Mailbox(localpart=localpart,
                      domain=domain_obj,
                      password=hash_ssha512(password))
    db.session.add(mailbox)

    db.session.commit()


@app.cli.command()
@click.argument('alias_yaml', type=click.File('r'))
def load_data(alias_yaml):
    data = yaml.safe_load(alias_yaml)

    class DomainLookup(dict):
        def __missing__(self, key):
            d = self[key] = Domain(name=key)
            db.session.add(d)
            return d

    domains = DomainLookup()

    for mailbox_addr, mailbox_info in data.items():
        localpart, at, domainpart = mailbox_addr.partition('@')
        password = mailbox_info['passwd']
        aliases = mailbox_info.get('aliases', ())

        mailbox = Mailbox(localpart=localpart,
                          domain=domains[domainpart],
                          password=password)
        db.session.add(mailbox)

        for alias in aliases:
            localpart, at, domainpart = alias.partition('@')
            alias = Alias(localpart=localpart,
                          domain=domains[domainpart],
                          mailbox=mailbox)
            db.session.add(alias)

    db.session.commit()
