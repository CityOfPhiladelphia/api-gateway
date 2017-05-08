from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy import func

db = SQLAlchemy()

class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String)
    active = db.Column(db.Boolean, nullable=False)
    owner_name = db.Column(db.String)
    contact_name = db.Column(db.String)
    contact_email = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now(),
                           server_onupdate=func.now())

    ## TODO: add columns for custom rate limit

    def __init__(self, active, owner_name, contact_name, contact_email, expires_at):
        self.active = active
        self.owner_name = owner_name
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.expires_at = expires_at

    def __repr__(self):
        return '<Key id: {} active: {} owner_name: {}>'.format(self.id, \
                                                               self.active, \
                                                               self.owner_name)

class Ban(db.Model):
    __tablename__ = 'bans'

    id = db.Column(db.Integer, primary_key=True)
    cidr = db.Column(CIDR, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now(),
                           server_onupdate=func.now())

    ## TODO: validate CIDR blocks

    def __init__(self, cidr, active, expires_at):
        self.cidr = cidr
        self.active = active
        self.expires_at = expires_at

    def __repr__(self):
        return '<Ban id: {} cidr: {} active: {} expires_at: {}>'.format(self.id, \
                                                                               self.cidr, \
                                                                               self.active, \
                                                                               self.expires_at)
