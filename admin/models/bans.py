from sqlalchemy.dialects.postgresql import ARRAY

from app import db

class Ban(db.Model):
    __tablename__ = 'bans'

    id = db.Column(db.Integer, primary_key=True)
    cidr_blocks = db.Column(ARRAY(db.String))
    active = db.Column(db.Boolean, nullable=False)
    expires_at = db.Column(db.Datetime)
    created_at = db.Column(db.Datetime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.Datetime,
                           nullable=False,
                           server_default=func.now(),
                           server_onupdate=func.now())

    ## TODO: validate CIDR blocks

    def __init__(self, owner_name, contact_name, contact_email, expires_at):
        self.cidr_blocks = owner_name
        self.active = contact_name
        self.expires_at = expires_at

    def __repr__(self):
        return '<Ban id: {} cidr_blocks: {} active: {} expires_at: {}>'.format(self.id, \
                                                                               self.cidr_blocks, \
                                                                               self.active \
                                                                               self.expires_at)

