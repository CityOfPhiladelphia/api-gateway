from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy import func, Index

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
                           onupdate=func.now())

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
    active = db.Column(db.Boolean, nullable=False)
    title = db.Column(db.String)
    description = db.Column(db.String)
    cidr_blocks = db.relationship('CIDRBlock',
                                  backref='ban',
                                  passive_deletes=True # required to cascade deletes
                                  # ,
                                  # lazy='joined'
                                  )
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now(),
                           onupdate=func.now())

    def __init__(self, active, title, description, cidr_blocks, expires_at):
        self.active = active
        self.title = title
        self.description = description
        self.expires_at = expires_at

        for block in cidr_blocks:
            self.cidr_blocks.append(block)

    def __repr__(self):
        return '<Ban id: {} cidr: {} active: {} expires_at: {}>'.format(self.id, \
                                                                        self.active, \
                                                                        self.title, \
                                                                        self.expires_at)

class CIDRBlock(db.Model):
    __tablename__ = 'cider_blocks'

    ## TODO: validate CIDR blocks

    id = db.Column(db.Integer, primary_key=True)
    ban_id = db.Column(db.Integer, db.ForeignKey('bans.id', ondelete='CASCADE'))
    cidr = db.Column(CIDR, nullable=False)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=func.now(),
                           onupdate=func.now())

    def __init__(self, cidr):
        self.cidr = cidr

    def __repr__(self):
        return '<CIDRBlock id: {} ban_id: {} cidr: {}>'.format(self.id, self.ban_id, self.cidr)

Index('idx_cidr', CIDRBlock.__table__.c.cidr, postgresql_using='gist', postgresql_ops={'cidr': 'inet_ops'})
