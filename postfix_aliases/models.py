from email.headerregistry import Address

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from .password import hash_ssha512


db = SQLAlchemy()


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    @classmethod
    def get(cls, name):
        return cls.query.filter(cls.name == name.lower()).first()

    @classmethod
    def new(cls, name):
        self = cls(name=name.lower())
        db.session.add(self)
        return self

    @classmethod
    def ensure(cls, name):
        return cls.get(name) or cls.new(name)

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

    @classmethod
    def get(cls, addr):
        addr = Address(addr_spec=addr)
        return cls.query.join(Domain).filter(
            cls.localpart == addr.username.lower(),
            Domain.name == addr.domain.lower()).first()

    @classmethod
    def new(cls, addr, password=None):
        addr = Address(addr_spec=addr)
        domain = Domain.ensure(addr.domain)
        self = cls(localpart=addr.username.lower(),
                   domain=domain,
                   password='')
        if password is not None:
            self.password = hash_ssha512(password)
        db.session.add(self)
        return self

    def add_alias(self, addr):
        addr = Address(addr_spec=addr)
        alias = Alias(localpart=addr.username.lower(),
                      domain=Domain.get(addr.domain),
                      mailbox=self)
        db.session.add(alias)
        return alias

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
