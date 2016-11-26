from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)


class Mailbox(UserMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint('localpart', 'domain_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    localpart = db.Column(db.String(128))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain', backref='mailboxes')
    password = db.Column(db.String(128))


class Alias(db.Model):
    __table_args__ = (
        db.UniqueConstraint('localpart', 'domain_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    localpart = db.Column(db.String(128))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain', backref='aliases')
    mailbox_id = db.Column(db.Integer, db.ForeignKey('mailbox.id'))
    mailbox = db.relationship('Mailbox', backref='aliases')
