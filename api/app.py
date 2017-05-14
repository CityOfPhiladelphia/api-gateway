import os

import flask
from flask_restful import Resource, Api
from flask_login import LoginManager

from models import db, User
import resources

app = flask.Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG', False)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SESSION_COOKIE_NAME'] = 'gatewaysession'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = os.getenv('FLASK_SESSION_DOMAIN', None)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_SESSION_SECURE', False)
app.secret_key = os.getenv('FLASK_SESSION_SECRET_KEY')

db.init_app(app)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

## TODO: gateway API access
## TODO: CSRF support using header?

with app.app_context():
    db.create_all() ## TODO: move to separate migration script? like https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

    api.add_resource(resources.UserListResource, '/users')
    api.add_resource(resources.UserResource, '/users/<int:instance_id>')
    api.add_resource(resources.SessionResource, '/session')
    api.add_resource(resources.BanListResource, '/bans')
    api.add_resource(resources.BanResource, '/bans/<int:instance_id>')
    api.add_resource(resources.CIDRBlockListResource, '/bans/cidr-blocks')
    api.add_resource(resources.CIDRBlockResource, '/bans/cidr-blocks/<int:instance_id>')
    api.add_resource(resources.KeyListResource, '/keys')
    api.add_resource(resources.KeyResource, '/keys/<int:instance_id>')

## dev server
if __name__ == '__main__':
    app.run(host='0.0.0.0')
