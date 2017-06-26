from functools import wraps
import binascii
import os

from marshmallow_sqlalchemy import ModelSchema, field_for
from marshmallow import Schema, fields, validates_schema, ValidationError
from flask import request
from flask_restful import Resource, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.dialects.postgresql import CIDR
from netaddr import IPNetwork
from itsdangerous import URLSafeSerializer
from restful_ben.resources import (
    BaseResource,
    RetrieveUpdateDeleteResource,
    QueryEngineMixin,
    CreateListResource
)
from restful_ben.auth import authorization, CSRF

from api_gateway.models import db, Ban, CIDRBlock, Key, User

csrf = CSRF()

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

user_roles = {
    'normal': ['GET'],
    'admin': ['POST','GET','PUT','DELETE']
}

def user_authorization(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(current_user, 'role'):
            role = current_user.role
        else:
            role = None
        
        if role and role in user_roles:
            if request.method in user_roles[role]:
                return func(*args, **kwargs)

        if role and 'instance_id' in kwargs and current_user.id == int(kwargs['instance_id']):
            return func(*args, **kwargs)

        abort(403)
    return wrapper

class UserResource(RetrieveUpdateDeleteResource):
    method_decorators = [csrf.csrf_check, user_authorization, login_required]

    single_schema = user_schema
    model = User
    session = db.session

class UserListResource(QueryEngineMixin, CreateListResource):
    method_decorators = [csrf.csrf_check, user_authorization, login_required]

    query_engine_exclude_fields = ['hashed_password', 'password']
    single_schema = user_schema
    many_schema = users_schema
    model = User
    session = db.session

## CIDR Blocks

class CIDRBlockSchema(ModelSchema):
    class Meta:
        model = CIDRBlock
        sqla_session = db.session

    id = field_for(Ban, 'id', dump_only=True)
    cidr = fields.Str()
    created_at = field_for(Ban, 'created_at', dump_only=True)
    updated_at = field_for(Ban, 'updated_at', dump_only=True)

    @validates_schema
    def validate_cidr(self, data):
        try:
            IPNetwork(data['cidr']) # will raise an exception on an invalid network
        except:
            raise ValidationError("'{}' is an invalid CIDR".format(data['cidr']))

cidr_block_schema = CIDRBlockSchema()
cidr_blocks_schema = CIDRBlockSchema(many=True)

cidr_block_authorization = authorization({
    'gateway': ['GET'],
    'normal': ['GET'],
    'admin': ['POST','GET','DELETE']
})

class CIDRBlockResource(RetrieveUpdateDeleteResource):
    method_decorators = [csrf.csrf_check, cidr_block_authorization, login_required]
    methods = ['GET','DELETE']
    single_schema = cidr_block_schema
    model = CIDRBlock
    session = db.session

class CIDRBlockListResource(QueryEngineMixin, BaseResource):
    method_decorators = [csrf.csrf_check, cidr_block_authorization, login_required]
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

ban_authorization = authorization({
    'gateway': ['GET'],
    'normal': ['GET'],
    'admin': ['POST','PUT','GET','DELETE']
})

class BanResource(RetrieveUpdateDeleteResource):
    method_decorators = [csrf.csrf_check, ban_authorization, login_required]
    single_schema = ban_schema_put_get
    model = Ban
    session = db.session

class BanListResource(QueryEngineMixin, CreateListResource):
    method_decorators = [csrf.csrf_check, ban_authorization, login_required]
    single_schema = ban_schema
    many_schema = bans_schema
    model = Ban
    session = db.session

## Keys

class KeySchema(ModelSchema):
    class Meta:
        model = Key
        exclude = ['key']

    id = field_for(Key, 'id', dump_only=True)
    created_at = field_for(Key, 'created_at', dump_only=True)
    updated_at = field_for(Key, 'updated_at', dump_only=True)

class KeyCreateSchema(KeySchema):
    class Meta:
        model = Key

    key = field_for(Key, 'key', dump_only=True)

key_schema = KeySchema()
key_create_schema = KeyCreateSchema()
keys_schema = KeySchema(many=True)

key_authorization = authorization({
    'gateway': ['GET'],
    'normal': ['GET'],
    'admin': ['POST','PUT','GET','DELETE']
})

class KeyResource(RetrieveUpdateDeleteResource):
    method_decorators = [csrf.csrf_check, key_authorization, login_required]
    single_schema = key_schema
    model = Key
    session = db.session

class KeyListResource(QueryEngineMixin, CreateListResource):
    method_decorators = [csrf.csrf_check, key_authorization, login_required]
    single_schema = key_create_schema
    many_schema = keys_schema
    model = Key
    session = db.session
