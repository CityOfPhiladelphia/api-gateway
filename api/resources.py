from marshmallow_sqlalchemy import ModelSchema, field_for
from marshmallow import Schema, fields
from flask import request
from flask_restful import Resource, abort
from flask_login import login_user, logout_user
from sqlalchemy.dialects.postgresql import CIDR

from models import db, Ban, CIDRBlock, Key, User
from restful import RetrieveUpdateDeleteResource, CreateListResource, QueryEngineMixin, BaseResource

## Users

class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ['hashed_password']

    id = field_for(User, 'id', dump_only=True)
    password = fields.Str(load_only=True)
    created_at = field_for(User, 'created_at', dump_only=True)
    updated_at = field_for(User, 'updated_at', dump_only=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UserResource(RetrieveUpdateDeleteResource):
    single_schema = user_schema
    model = User
    session = db.session

class UserListResource(QueryEngineMixin, CreateListResource):
    single_schema = user_schema
    many_schema = users_schema
    model = User
    session = db.session

## Sessions

class SessionSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

session_schema = SessionSchema()

class SessionResource(Resource):
    def post(self):
        raw_body = request.json
        session_load = session_schema.load(raw_body)

        if session_load.errors:
            abort(400, errors=session_load.errors)

        session = session_load.data

        user = db.session.query(User).filter(User.username == session['username']).first()

        if not user:
            abort(401, errors=['Not Authorized'])

        password_matches = user.verify_password(session['password'])
        if not password_matches:
            abort(401, errors=['Not Authorized'])

        login_user(user)

        return None, 204

    def delete(self):
        logout_user()

        return None, 204

## CIDR Blocks

class CIDRBlockSchema(ModelSchema):
    class Meta:
        model = CIDRBlock
        sqla_session = db.session

    id = field_for(Ban, 'id', dump_only=True)
    cidr = fields.Str()
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

cidr_block_schema = CIDRBlockSchema()
cidr_blocks_schema = CIDRBlockSchema(many=True)

class CIDRBlockResource(RetrieveUpdateDeleteResource):
    methods = ['GET','DELETE']
    single_schema = cidr_block_schema
    model = CIDRBlock
    session = db.session

class CIDRBlockListResource(QueryEngineMixin, BaseResource):
    many_schema = cidr_blocks_schema
    model = CIDRBlock
    session = db.session
    operator_overrides = {
        'cidr': {
            'contains': CIDRBlock.cidr.op('>>=')
        }
    }

## Bans

class BanSchema(ModelSchema):
    class Meta:
        model = Ban

    id = field_for(Ban, 'id', dump_only=True)
    cidr_blocks = fields.Nested(CIDRBlockSchema, many=True, required=True)
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

class BanSchemaPUTGET(BanSchema):
    cidr_blocks = fields.Nested(CIDRBlockSchema, dump_only=True, many=True)

ban_schema = BanSchema()
ban_schema_put_get= BanSchemaPUTGET()
bans_schema = BanSchema(many=True)

class BanResource(RetrieveUpdateDeleteResource):
    single_schema = ban_schema_put_get
    model = Ban
    session = db.session

class BanListResource(QueryEngineMixin, CreateListResource):
    single_schema = ban_schema
    many_schema = bans_schema
    model = Ban
    session = db.session

## Keys

class KeySchema(ModelSchema):
    class Meta:
        model = Key

    id = field_for(Key, 'id', dump_only=True)
    created_at = field_for(Key, 'created_at', dump_only=True)
    updated_at = field_for(Key, 'updated_at', dump_only=True)

key_schema = KeySchema()
keys_schema = KeySchema(many=True)

class KeyResource(RetrieveUpdateDeleteResource):
    single_schema = key_schema
    model = Key
    session = db.session

class KeyListResource(CreateListResource):
    single_schema = key_schema
    many_schema = keys_schema
    model = Key
    session = db.session
