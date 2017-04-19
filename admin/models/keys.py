from app import db

class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String)
    active = db.Column(db.Boolean, nullable=False)
    owner_name = db.Column(db.String)
    contact_name = db.Column(db.String)
    contact_email = db.Column(db.String)
    expires_at = db.Column(db.Datetime)
    created_at = db.Column(db.Datetime,
                           nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.Datetime,
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

