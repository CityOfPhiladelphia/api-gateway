import os

import pytest

os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/api_gateway_test'
os.environ['FLASK_SESSION_SECRET_KEY'] = 'test'
os.environ['CSRF_SECRET'] = 'test'
os.environ['GATEWAY_KEY'] = 'testtoken'

from api_gateway.app import app as app_orig
from api_gateway.models import db, User, Key, Ban, CIDRBlock

@pytest.fixture
def app():
    with app_orig.app_context():
        db.create_all()

    yield app_orig

    with app_orig.app_context():
        db.drop_all()

@pytest.fixture
def model_fixtures(app):
    with app.app_context():
        user1 = User(active=True, username='amadonna', password='foo', role='admin')
        db.session.add(user1)
        db.session.commit()

        key1 = Key(active=True, owner_name='jane doe')
        db.session.add(key1)
        db.session.commit()

        ban1 = Ban(active=True, title='foo', cidr_blocks=[CIDRBlock(cidr='10.0.0.0/16')])
        db.session.add(ban1)
        db.session.commit()
