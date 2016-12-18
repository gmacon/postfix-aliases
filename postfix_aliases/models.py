from email.headerregistry import Address

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)


class Mailbox(UserMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint('localpart', 'domain_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    localpart = db.Column(db.String(128))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain', backref='mailboxes')
    password = db.Column(db.String(128))

    def __str__(self):
        return str(Address(username=self.localpart,
                           domain=self.domain.name))

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


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

    def __str__(self):
        return str(Address(username=self.localpart,
                           domain=self.domain.name))

    def __repr__(self):
        return '<{}: {} for {}>'.format(self.__class__.__name__, self,
                                        self.mailbox)
