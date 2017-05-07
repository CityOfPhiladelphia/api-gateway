import os

import flask
from flask_restful import Resource, Api

from models import db
from resources import BanResource, BanListResource, KeyResource, KeyListResource

app = flask.Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG', False)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

db.init_app(app)
api = Api(app)

## TODO: login
## TODO: RBAC

with app.app_context():
    db.create_all() ## TODO: move to separate migration script? like https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

    ## TODO: anon = GET, logged in user = GET, admin = GET, POST, PUT, DELETE
    ## TODO: anon = GET, logged in user = GET, admin = GET, POST, PUT, DELETE
    ## TODO: filter out key in response except for POST
    ## TODO: GET by id or key

    api.add_resource(BanListResource, '/bans')
    api.add_resource(BanResource, '/bans/<instance_id>')
    api.add_resource(KeyListResource, '/keys')
    api.add_resource(KeyResource, '/keys/<key_id>')

if __name__ == '__main__':
    app.run()
