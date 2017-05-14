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
app.secret_key = os.getenv('FLASK_SESSION_SECRET_KEY')

db.init_app(app)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

## TODO: login
## TODO: RBAC

with app.app_context():
    db.create_all() ## TODO: move to separate migration script? like https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

    ## TODO: anon = GET, logged in user = GET, admin = GET, POST, PUT, DELETE
    ## TODO: anon = GET, logged in user = GET, admin = GET, POST, PUT, DELETE
    ## TODO: filter out key in response except for POST
    ## TODO: GET by id or key

    api.add_resource(resources.UserListResource, '/users')
    api.add_resource(resources.UserResource, '/users/<instance_id>')
    api.add_resource(resources.SessionResource, '/session')
    api.add_resource(resources.BanListResource, '/bans')
    api.add_resource(resources.BanResource, '/bans/<instance_id>')
    api.add_resource(resources.CIDRBlockListResource, '/bans/cidr-blocks')
    api.add_resource(resources.CIDRBlockResource, '/bans/cidr-blocks/<instance_id>')
    api.add_resource(resources.KeyListResource, '/keys')
    api.add_resource(resources.KeyResource, '/keys/<instance_id>')

## dev server
if __name__ == '__main__':
    app.run(host='0.0.0.0')
